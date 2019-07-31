from ahk import AHK, Hotkey


def main():
    ahk = AHK(executable_path='H:\\AutoHotkey_1.1.29.01\\AutoHotkeyU64.exe')

    key_combo = '^n'
    script = 'Run Notepad.exe'
    hotkey = Hotkey(ahk, key_combo, script)
    hotkey.start()


if __name__ == '__main__':
    main()