import getpass

from pynput import keyboard
from pystray import Icon, Menu, MenuItem
from json.decoder import JSONDecodeError
import PIL.Image
import rotatescreen
import json
import os
import sys


_active_screen_key = "active_screen"
_orientation_value_landscape = "landscape"
_orientation_value_landscape_flipped = "landscape_flipped"
_orientation_value_portrait = "portrait"
_orientation_value_portrait_flipped = "portrait_flipped"

debug_mode = sys.gettrace() is not None

user_name = getpass.getuser()
save_dir = os.path.join("C:\\Users", user_name, "Documents", "ScreenRotateControl")
settings_file_path = os.path.join(save_dir, "settings.json")
settings_data = {}
displays = rotatescreen.get_displays()


display_index_to_apply_rotation = 1     # default value


def get_active_screen():
    return displays[get_active_screen_index()]


def get_active_screen_index():
    return display_index_to_apply_rotation - 1


def get_default_settings():
    default_settings = {_active_screen_key: 1}
    for i in range(0, len(displays)):
        default_settings[str(i)] = _orientation_value_landscape
    return default_settings


def update_settings():
    with open(settings_file_path, "w+") as settings_write_file:
        json.dump(settings_data, settings_write_file, indent=4)


def apply_settings():
    global display_index_to_apply_rotation
    display_index_to_apply_rotation = int(settings_data[_active_screen_key])
    for i in range(0, len(displays)):
        screen_orientation = settings_data.get(str(i))
        if screen_orientation is not None:
            apply_rotation(displays[i], screen_orientation)


def apply_rotation(display, orientation):
    if orientation == _orientation_value_landscape:
        display.set_landscape()
    elif orientation == _orientation_value_landscape_flipped:
        display.set_landscape_flipped()
    elif orientation == _orientation_value_portrait:
        display.set_portrait()
    elif orientation == _orientation_value_portrait_flipped:
        display.set_portrait_flipped()
    settings_data[str(get_active_screen_index())] = orientation
    update_settings()


if not os.path.exists(save_dir):
    os.makedirs(save_dir)
try:
    with open(settings_file_path, "r") as settings_append_file:
        try:
            # setting exists
            settings_data = json.load(settings_append_file)
            apply_settings()
        except JSONDecodeError:
            # no setting was saved before this session
            debug_mode and print("no settings saved")
            pass
except FileNotFoundError:
    debug_mode and print("no such file exists")
    settings_data = get_default_settings()
    with open(settings_file_path, "w+") as temp:
        json.dump(settings_data, temp, indent=4)


def apply_change_display_index(i):
    global display_index_to_apply_rotation
    display_index_to_apply_rotation = i
    settings_data[_active_screen_key] = i
    update_settings()


def on_activate_hotkey(orientation):
    def inner():
        apply_rotation(get_active_screen(), orientation)
    return inner


def on_activate_hotkey_numbers(i):
    def inner():
        global display_index_to_apply_rotation
        if i <= len(displays):
            apply_change_display_index(i)
        tray_icon.update_menu()
    return inner


listener = keyboard.GlobalHotKeys({
    '<ctrl>+<alt>+<38>': on_activate_hotkey(_orientation_value_landscape),              # arrow-up
    '<ctrl>+<alt>+<40>': on_activate_hotkey(_orientation_value_landscape_flipped),      # arrow-down
    '<ctrl>+<alt>+<37>': on_activate_hotkey(_orientation_value_portrait),               # arrow-left
    '<ctrl>+<alt>+<39>': on_activate_hotkey(_orientation_value_portrait_flipped),       # arrow-right
    '<ctrl>+<alt>+1': on_activate_hotkey_numbers(1),
    '<ctrl>+<alt>+2': on_activate_hotkey_numbers(2),
    '<ctrl>+<alt>+3': on_activate_hotkey_numbers(3),
    '<ctrl>+<alt>+4': on_activate_hotkey_numbers(4),
    '<ctrl>+<alt>+5': on_activate_hotkey_numbers(5),
    '<ctrl>+<alt>+6': on_activate_hotkey_numbers(6),
    '<ctrl>+<alt>+7': on_activate_hotkey_numbers(7),
    '<ctrl>+<alt>+8': on_activate_hotkey_numbers(8),
    '<ctrl>+<alt>+9': on_activate_hotkey_numbers(9),
})
listener.start()


def on_click_exit(icon, item):
    listener.stop()
    icon.stop()


def get_active_screen_state(i):
    def inner(item):
        return display_index_to_apply_rotation == i
    return inner


def set_active_screen_state(i):
    def inner(icon, item):
        apply_change_display_index(i)
    return inner


def get_orientation_state(orientation):
    def inner(item):
        return settings_data[str(get_active_screen_index())] == orientation
    return inner


def set_orientation_state(display, orientation):
    def inner(icon, item):
        apply_rotation(display, orientation)
    return inner


tray_icon = Icon(
    "Screen Rotation Control",
    PIL.Image.open("icon_rotate.png"),
    menu=Menu(
        MenuItem(
            "Apply rotation to:",
            Menu(
                lambda: (
                    MenuItem(
                        "Display #%d" % i,
                        set_active_screen_state(i),
                        checked=get_active_screen_state(i),
                        radio=True,
                    ) for i in range(1, len(displays)+1)
                )
            )
        ),
        MenuItem(
            "Screen orientation:",
            Menu(
                lambda: (
                    MenuItem(
                        title,
                        set_orientation_state(
                            get_active_screen(),
                            orientation
                        ),
                        checked=get_orientation_state(orientation),
                        radio=True
                    ) for title, orientation in
                    {
                        "Landscape": _orientation_value_landscape,
                        "Landscape_Flipped": _orientation_value_landscape_flipped,
                        "Portrait": _orientation_value_portrait,
                        "Portrait_Flipped": _orientation_value_portrait_flipped
                    }.items()
                )
            )
        ),
        MenuItem("Exit", on_click_exit)
    )
)
tray_icon.run()


# Build command:
# pyinstaller -w -F main.py
