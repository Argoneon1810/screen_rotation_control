import getpass

from pynput import keyboard
from pystray import Icon, Menu, MenuItem
from json.decoder import JSONDecodeError
from lang import translations as tr
import PIL.Image
import rotatescreen
import json
import os
import sys


_key_active_screen = "active_screen"
_icon_file_name = "icon_rotate.ico"
_key_language = "lang"
_value_orientation_landscape = "landscape"
_value_orientation_landscape_flipped = "landscape_flipped"
_value_orientation_portrait = "portrait"
_value_orientation_portrait_flipped = "portrait_flipped"
_debug_mode = sys.gettrace() is not None
_user_name = getpass.getuser()
_save_dir = os.path.join("C:\\Users", _user_name, "Documents", "ScreenRotateControl")
_settings_file_path = os.path.join(_save_dir, "settings.json")
_settings_data = {}
_displays = rotatescreen.get_displays()
_current_translation = {}
_display_index_to_apply_rotation = 1     # default value


tray_icon: Icon
listener: keyboard.GlobalHotKeys


def prepare_exit():
    listener.stop()
    tray_icon.stop()


def get_active_screen():
    return _displays[get_active_screen_index()]


def get_active_screen_index():
    return _display_index_to_apply_rotation - 1


def get_default_settings():
    default_settings = {
        _key_language: tr.translations.keys()[0],
        _key_active_screen: 1
    }
    for i in range(0, len(_displays)):
        default_settings[str(i)] = _value_orientation_landscape
    return default_settings


def update_settings():
    with open(_settings_file_path, "w+") as settings_write_file:
        json.dump(_settings_data, settings_write_file, indent=4)


def apply_settings():
    global _display_index_to_apply_rotation
    _display_index_to_apply_rotation = int(_settings_data[_key_active_screen])
    for i in range(0, len(_displays)):
        screen_orientation = _settings_data.get(str(i))
        if screen_orientation is not None:
            apply_rotation(_displays[i], screen_orientation)


def apply_rotation(display, orientation):
    if orientation == _value_orientation_landscape:
        display.set_landscape()
    elif orientation == _value_orientation_landscape_flipped:
        display.set_landscape_flipped()
    elif orientation == _value_orientation_portrait:
        display.set_portrait()
    elif orientation == _value_orientation_portrait_flipped:
        display.set_portrait_flipped()
    _settings_data[str(get_active_screen_index())] = orientation
    update_settings()


def get_text(key):
    if _current_translation is not {}:
        return _current_translation[key]
    else:
        return get_default_translation()[key]


def change_locale(new_locale):
    _settings_data[_key_language] = new_locale
    update_settings()


def get_default_locale():
    return list(tr.translations.keys())[0]


def get_default_translation():
    return tr.translations.get(get_default_locale())


def get_settings():
    global _settings_data
    if not os.path.exists(_save_dir):
        os.makedirs(_save_dir)
    try:
        with open(_settings_file_path, "r") as settings_append_file:
            try:
                # setting exists
                _settings_data = json.load(settings_append_file)
                apply_settings()
            except JSONDecodeError:
                # no setting was saved before this session
                _debug_mode and print(get_text(tr.key_debug_no_settings_saved))
                pass
    except FileNotFoundError:
        _debug_mode and print(get_text(tr.key_no_such_file_exists))
        _settings_data = get_default_settings()
        with open(_settings_file_path, "w+") as temp:
            json.dump(_settings_data, temp, indent=4)


def get_translation():
    global _current_translation
    locale = _settings_data.get(_key_language)
    if locale is None:
        locale = get_default_locale()
        change_locale(locale)
    _current_translation = tr.translations[locale]


def apply_change_display_index(i):
    global _display_index_to_apply_rotation
    _display_index_to_apply_rotation = i
    _settings_data[_key_active_screen] = i
    update_settings()


def on_activate_hotkey(orientation):
    def inner():
        apply_rotation(get_active_screen(), orientation)
    return inner


def on_activate_hotkey_numbers(i):
    def inner():
        global _display_index_to_apply_rotation
        if i <= len(_displays):
            apply_change_display_index(i)
        tray_icon.update_menu()
    return inner


def on_click_exit(icon, item):
    prepare_exit()


def get_active_screen_state(i):
    def inner(item):
        return _display_index_to_apply_rotation == i
    return inner


def set_active_screen_state(i):
    def inner(icon, item):
        apply_change_display_index(i)
    return inner


def get_orientation_state(orientation):
    def inner(item):
        return _settings_data[str(get_active_screen_index())] == orientation
    return inner


def set_orientation_state(display, orientation):
    def inner(icon, item):
        apply_rotation(display, orientation)
    return inner


def get_translation_state(locale_option):
    def inner(item):
        return _settings_data[_key_language] == locale_option
    return inner


def set_translation_state(locale_option):
    def inner(icon, item):
        change_locale(locale_option)
        get_translation()
        tray_icon.update_menu()
    return inner


def init_and_start_hotkey_listener():
    global listener
    listener = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+<38>': on_activate_hotkey(_value_orientation_landscape),  # arrow-up
        '<ctrl>+<alt>+<40>': on_activate_hotkey(_value_orientation_landscape_flipped),  # arrow-down
        '<ctrl>+<alt>+<37>': on_activate_hotkey(_value_orientation_portrait),  # arrow-left
        '<ctrl>+<alt>+<39>': on_activate_hotkey(_value_orientation_portrait_flipped),  # arrow-right
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


def init_and_start_tray_icon():
    global tray_icon
    tray_icon = Icon(
        lambda text: get_text(tr.key_application_title),
        PIL.Image.open(_icon_file_name),
        menu=Menu(
            MenuItem(
                lambda text: get_text(tr.key_apply_rotation_to),
                Menu(
                    lambda: (
                        MenuItem(
                            get_text(tr.key_display_index) % i,
                            set_active_screen_state(i),
                            checked=get_active_screen_state(i),
                            radio=True,
                        ) for i in range(1, len(_displays) + 1)
                    )
                )
            ),
            MenuItem(
                lambda text: get_text(tr.key_screen_orientation),
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
                            get_text(tr.key_landscape): _value_orientation_landscape,
                            get_text(tr.key_landscape_flipped): _value_orientation_landscape_flipped,
                            get_text(tr.key_portrait): _value_orientation_portrait,
                            get_text(tr.key_portrait_flipped): _value_orientation_portrait_flipped
                        }.items()
                    )
                )
            ),
            MenuItem(
                lambda text: get_text(tr.key_translations),
                Menu(
                    lambda: (
                        MenuItem(
                            translations,
                            set_translation_state(translations),
                            checked=get_translation_state(translations),
                            radio=True
                        ) for translations in tr.translations.keys()
                    )
                )
            ),
            MenuItem(lambda text: get_text(tr.key_exit), on_click_exit)
        )
    )
    tray_icon.run()


def main():
    get_settings()
    get_translation()
    init_and_start_hotkey_listener()
    init_and_start_tray_icon()


main()


# Build command:
# pyinstaller -w -F main.py
