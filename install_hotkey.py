import os
import webbrowser

def main():
    print("Immich Explorer Selector – AutoHotkey Installer\n")

    have_ahk = input("Do you already have AutoHotkey installed? (y/n): ").strip().lower()

    if have_ahk != "y":
        print("\nOpening AutoHotkey download page...")
        webbrowser.open("https://www.autohotkey.com/download/ahk-install.exe")
        print("Please install AutoHotkey v1.1, then re-run this installer.")
        return
    python_cmd = input(
        "Python command to use (e.g. py, python, or full path) [py]: "
    ).strip()

    if not python_cmd:
        python_cmd = "py"


    user_home = os.path.expanduser("~")
    ahk_dir = os.path.join(user_home, "Documents", "AutoHotkey")
    target_path = os.path.join(user_home, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "ImmichSelect.lnk")
    os.makedirs(ahk_dir, exist_ok=True)

    ahk_path = os.path.join(ahk_dir, "ImmichSelect.ahk")

    immich_script = input("Full path to immich_to_smb.py (user folder or other working directory):\n> ").strip().strip('"')

    if not os.path.isfile(immich_script):
        print("Error: immich_to_smb.py not found.")
        return

    immich_script = immich_script.replace('"', '""')

    ahk_contents = (
        "; Immich → Explorer selector\n"
        "; Hotkey: Ctrl + Alt + I\n\n"
        "^!i::\n"
        "    ; Save clipboard\n"
        "    ClipSaved := ClipboardAll\n"
        "    Clipboard := \"\"\n\n"
        "    ; Focus address bar\n"
        "    Send ^l\n"
        "    Sleep 60\n\n"
        "    Send ^c\n"
        "    Sleep 60\n\n"
        "    url := Clipboard\n\n"
        "    ; Restore clipboard\n"
        "    Clipboard := ClipSaved\n"
        "    ClipSaved := \"\"\n\n"
        "    if (url = \"\")\n"
        "    {\n"
        "        SoundBeep, 750\n"
        "        return\n"
        "    }\n\n"
        "    python := \"" + python_cmd.replace('"', '""') + "\"\n"

        "    script := \"" + immich_script + "\"\n\n"
        "    Run, % python \" \"\"\" script \"\"\" \"\"\" url \"\"\"\", , Hide\n"
        "return\n"
    )

    with open(ahk_path, "w", encoding="utf-8") as f:
        f.write(ahk_contents)

    print( )
    print( )
    print( )
    print("\nYou're almost done. Go to \\Documents\\AutoHotkey and open the script with AutoHotkey.")
    print("Written to:")
    print(" ", ahk_path)
    print("\nIf you have v2.0, you will be asked upon opening to download v.1.1")
    print( )
    print( )
    print( )
    print("\nTo enable the hotkey on startup, copy-paste the following into the Command Prompt:\n")
    print(
    f'powershell -NoProfile -Command '
    f'"$WshShell = New-Object -ComObject WScript.Shell; '
    f'$Shortcut = $WshShell.CreateShortcut(\'{target_path}\'); '
    f'$Shortcut.TargetPath = \'C:\\Program Files\\AutoHotkey\\v1.1.37.02\\AutoHotkeyU64.exe\'; '
    f'$Shortcut.Arguments = \'"{ahk_path}\"'; '
    f'$Shortcut.WorkingDirectory = \'{ahk_dir}\'; '
    f'$Shortcut.Save()"'
    )


if __name__ == "__main__":
    main()