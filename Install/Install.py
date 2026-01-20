import os
from textwrap import dedent

def main():
    print("Immich → SMB path translator installer")
    print("Installing CLI based tool to open Immich photos in Windows File Explorer\n")

    immich_url = input("Immich server URL (e.g. http://192.168.1.7:2283): ").strip().rstrip("/")

    print("\nDefine Immich external libraries.")
    print("Type 'done' when finished.\n")

    libraries = []

    while True:
        immich_base = input("Immich base path (e.g. /files/extlibraryname): ").strip()
        if immich_base.lower() == "done":
            break

        smb_base = input("SMB base library path (e.g. Z:\\smblibraryname). Do not use quotes for spaces: ").strip()
        libraries.append((immich_base, smb_base))
        print("Added.\n")

    if not libraries:
        print("No libraries defined. Aborting.")
        return

    output_script = "immich_to_smb.py"

    mapping_lines = [
        f"    os.path.normpath({ib!r}): os.path.normpath({sb!r}),"
        for ib, sb in libraries
    ]

    script_contents = dedent(f"""\
import os
import sys
import re
import json
import urllib.request
import subprocess

IMMICH_URL = {immich_url!r}

LIBRARY_MAP = {{
{chr(10).join(mapping_lines)}
}}

UUID_RE = re.compile(
    r"[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}}"
)

def translate_immich_path(immich_file_path: str) -> str:
    immich_file_path = os.path.normpath(immich_file_path)

    for immich_base, smb_base in LIBRARY_MAP.items():
        if immich_file_path.startswith(immich_base):
            rel = os.path.relpath(immich_file_path, immich_base)
            return os.path.join(smb_base, rel)

    raise ValueError("Path does not match any configured Immich library")

def extract_asset_id(input_str: str) -> str | None:
    m = UUID_RE.search(input_str)
    return m.group(0) if m else None

def fetch_asset_original_path(asset_id: str) -> str:
    api_key = os.environ.get("IMMICH_FE_API_KEY")
    if not api_key:
        raise RuntimeError("IMMICH_FE_API_KEY environment variable not set")

    url = f"{{IMMICH_URL}}/api/assets/{{asset_id}}"
    req = urllib.request.Request(
        url,
        headers={{"x-api-key": api_key}}
    )

    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)

    if "originalPath" not in data:
        raise RuntimeError("Asset response missing originalPath")

    return data["originalPath"]

def select_in_explorer(path: str):
    if os.name != "nt":
        raise RuntimeError("Explorer selection is only supported on Windows")

    subprocess.run(
        ["explorer.exe", "/select,", os.path.normpath(path)],
        check=False
    )

def main():
    args = sys.argv[1:]

    print_only = False
    if args and args[0] == "--print-only":
        print_only = True
        args = args[1:]

    if len(args) != 1:
        print("Usage:")
        print("  py immich_to_smb.py [--print-only] <immich path | asset id | immich URL>")
        sys.exit(1)

    arg = args[0]

    try:
        if arg.startswith("/"):
            smb_path = translate_immich_path(arg)
        else:
            asset_id = extract_asset_id(arg)
            if not asset_id:
                raise RuntimeError("Input is not a valid Immich path, asset ID, or URL")

            immich_path = fetch_asset_original_path(asset_id)
            smb_path = translate_immich_path(immich_path)

        print(smb_path)

        if not print_only:
            select_in_explorer(smb_path)

    except Exception as e:
        print("Error:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()
""")

    with open(output_script, "w", encoding="utf-8") as f:
        f.write(script_contents)

    print("\nYou're halfway done.")
    print(f"Created: {output_script}")
    print("\nBehavior:")
    print("  - Prints SMB path when activated by CLI (py immich_to_smb.py /files/.../image.jpg)")
    print("  - Selects file in Explorer")
    print("  - --print-only disables Explorer interaction")
    print("\nType \"py install_hotkey.py\" to install AutoHotkey script")

if __name__ == "__main__":
    main()
