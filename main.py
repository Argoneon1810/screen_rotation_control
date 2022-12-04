from pynput import keyboard
from pystray import Icon, Menu, MenuItem
import PIL.Image
import rotatescreen


def on_activate_hotkey_landscape():
    displays[display_index_to_apply_rotation - 1].set_landscape()


def on_activate_hotkey_landscape_flipped():
    displays[display_index_to_apply_rotation - 1].set_landscape_flipped()


def on_activate_hotkey_portrait():
    displays[display_index_to_apply_rotation - 1].set_portrait()


def on_activate_hotkey_portrait_flipped():
    displays[display_index_to_apply_rotation - 1].set_portrait_flipped()


def on_activate_hotkey_numbers(i):
    def inner():
        global display_index_to_apply_rotation
        if i <= len(displays):
            display_index_to_apply_rotation = i
        tray_icon.update_menu()
    return inner


listener = keyboard.GlobalHotKeys({
    '<ctrl>+<alt>+<38>': on_activate_hotkey_landscape,              # up
    '<ctrl>+<alt>+<40>': on_activate_hotkey_landscape_flipped,      # down
    '<ctrl>+<alt>+<37>': on_activate_hotkey_portrait,               # left
    '<ctrl>+<alt>+<39>': on_activate_hotkey_portrait_flipped,       # right
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


displays = rotatescreen.get_displays()


def on_click_exit(icon, item):
    listener.stop()
    icon.stop()


def set_state(i):
    def inner(icon, item):
        global display_index_to_apply_rotation
        display_index_to_apply_rotation = i
    return inner


def get_state(i):
    def inner(item):
        return display_index_to_apply_rotation == i
    return inner


display_index_to_apply_rotation = 1
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
                        set_state(i),
                        checked=get_state(i),
                        radio=True,
                    ) for i in range(1, len(displays)+1)
                )
            )
        ),
        MenuItem("Exit", on_click_exit)
    )
)
tray_icon.run()


# pyinstaller -w -F main.py
