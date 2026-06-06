# ============================================================
#  Nexus Mods Auto-Upload Script
#  Author: StretchCGB
#  Mod: FH6 Head Tracking - tobii eye tracker and webcam
#  Uses: Nexus Mods v3 API
#
#  Setup:
#    1. pip install requests
#    2. Copy config.example.ini -> config.ini
#    3. Add your API key to config.ini
#    4. Get your FILE_GROUP_ID from your mod's Files tab
#       -> click "API Info" next to any existing file
#    5. python nexus_upload.py
#
#  Never commit config.ini to GitHub (it's in .gitignore)
# ============================================================

import requests
import configparser
import os
import sys
import math

# ============================================================
#  CONFIGURATION — edit these for your mod
# ============================================================

GAME_DOMAIN   = "forzahorizon6"
MOD_ID        = 288
FILE_GROUP_ID = 7487192   # StretchCGB - FH6 Head Tracking
API_BASE      = "https://api.nexusmods.com/v3"
API_V1_BASE   = "https://api.nexusmods.com/v1"
CONFIG_FILE   = "config.ini"
CHUNK_SIZE    = 10 * 1024 * 1024  # 10MB chunks

# Default zip to upload — override at prompt
DEFAULT_ZIP   = "FH6-HeadTracking-v1.2.0-NEXUS.zip"

# ============================================================
#  HELPERS
# ============================================================

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("")
        print("  [ERROR] config.ini not found.")
        print("  Copy config.example.ini to config.ini and fill in your API key.")
        print("  Get it from: https://www.nexusmods.com/users/myaccount?tab=api")
        print("")
        input("  Press Enter to exit...")
        sys.exit(1)

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)

    try:
        key = cfg["nexus"]["api_key"].strip()
        if not key or key == "YOUR_API_KEY_HERE":
            print("  [ERROR] API key not set in config.ini")
            sys.exit(1)
        return key
    except KeyError:
        print("  [ERROR] config.ini missing [nexus] section or api_key.")
        sys.exit(1)

def headers(api_key):
    return {
        "apikey":     api_key,
        "User-Agent": "FH6-HeadTracking-Uploader/1.2 (StretchCGB)"
    }

def validate_key(api_key):
    print("  Validating API key...")
    r = requests.get(
        "{}/users/validate.json".format(API_V1_BASE),
        headers=headers(api_key), timeout=10
    )
    if r.status_code == 200:
        u = r.json()
        print("  [OK] Signed in as: {} ({})".format(
            u.get("name", "?"),
            "Premium" if u.get("is_premium") else "Free"
        ))
        return True
    print("  [ERROR] API key rejected ({})".format(r.status_code))
    return False

def get_file_group_id(api_key):
    """Fetch existing files and let user pick a group, or enter manually."""
    r = requests.get(
        "{}/games/{}/mods/{}/files.json".format(API_V1_BASE, GAME_DOMAIN, MOD_ID),
        headers=headers(api_key), timeout=10
    )
    if r.status_code == 200:
        files = r.json().get("files", [])
        if files:
            print("")
            print("  Existing files on your mod page:")
            for f in files:
                print("    File ID: {:8}  Group ID: {:8}  {}  v{}".format(
                    f.get("file_id", "?"),
                    f.get("category_id", "?"),
                    f.get("name", "?"),
                    f.get("version", "?")
                ))
            print("")
            print("  To get the FILE GROUP ID:")
            print("  Go to your Nexus mod page -> Files tab -> click 'API Info'")
            print("  next to any existing file. Look for 'file_group_id'.")

    group_id = input("\n  Enter FILE_GROUP_ID: ").strip()
    if not group_id:
        print("  [ERROR] File group ID is required.")
        sys.exit(1)
    return group_id

# ============================================================
#  UPLOAD — chunked multipart using v3 API
# ============================================================

def upload_file(api_key, zip_path, file_group_id, version, display_name, description, category):
    file_size = os.path.getsize(zip_path)
    filename  = os.path.basename(zip_path)
    num_chunks = math.ceil(file_size / CHUNK_SIZE)

    print("")
    print("  File:      {}".format(filename))
    print("  Size:      {:.1f} MB".format(file_size / 1024 / 1024))
    print("  Chunks:    {}".format(num_chunks))
    print("  Version:   {}".format(version))
    print("  Category:  {}".format(category))
    print("")

    with open(zip_path, "rb") as f:
        for chunk_num in range(num_chunks):
            chunk_data  = f.read(CHUNK_SIZE)
            chunk_start = chunk_num * CHUNK_SIZE
            chunk_end   = chunk_start + len(chunk_data) - 1

            sys.stdout.write("\r  Uploading chunk {}/{}...".format(chunk_num + 1, num_chunks))
            sys.stdout.flush()

            upload_headers = {**headers(api_key), **{
                "Content-Type":        "application/octet-stream",
                "Content-Range":       "bytes {}-{}/{}".format(chunk_start, chunk_end, file_size),
                "X-File-Name":         filename,
                "X-File-Size":         str(file_size),
                "X-File-Group-Id":     str(file_group_id),
                "X-File-Version":      version,
                "X-File-Display-Name": display_name,
                "X-File-Description":  description,
                "X-File-Category":     category,
                "X-Mod-Id":            str(MOD_ID),
                "X-Game-Domain":       GAME_DOMAIN,
            }}

            r = requests.post(
                "{}/files/upload".format(API_BASE),
                data=chunk_data,
                headers=upload_headers,
                timeout=120
            )

    if r.status_code not in [200, 201, 206]:
                print("\n  [ERROR] Chunk {} failed: {}".format(chunk_num + 1, r.status_code))
                print("  Response body: {}".format(r.text[:500]))
                print("  Endpoint used: {}".format(API_BASE + "/files/upload"))
                print("")
                print("  If you see 404, the endpoint URL may have changed.")
                print("  Check: https://api-docs.nexusmods.com/ for the current upload path.")
                sys.exit(1)

    print("\n  [OK] All chunks uploaded!")
    return True

# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 58)
    print("  Nexus Mods Auto-Upload — FH6 Head Tracking")
    print("  Mod ID: {}   Game: {}".format(MOD_ID, GAME_DOMAIN))
    print("  API:    v3 (official Nexus upload endpoint)")
    print("=" * 58)
    print("")

    api_key = load_config()

    if not validate_key(api_key):
        sys.exit(1)

    print("")

    # File to upload - search common locations
    zip_input = input("  Zip to upload [{}]: ".format(DEFAULT_ZIP)).strip()
    zip_name  = zip_input if zip_input else DEFAULT_ZIP

    # Search for the zip in common locations
    search_paths = [
        zip_name,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), zip_name),
        os.path.join(os.path.expanduser("~"), "Desktop", "fh6Xtobii", zip_name),
        os.path.join(os.path.expanduser("~"), "Desktop", zip_name),
        os.path.join(os.path.expanduser("~"), "Downloads", zip_name),
    ]

    zip_path = None
    for p in search_paths:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            zip_path = p
            break

    if not zip_path:
        print("  [ERROR] Could not find '{}' in:".format(zip_name))
        for p in search_paths:
            exists = "EXISTS" if os.path.exists(p) else "not found"
            size   = " ({} bytes)".format(os.path.getsize(p)) if os.path.exists(p) else ""
            print("    {} - {}{}".format(p, exists, size))
        print("")
        print("  Please enter the FULL path to the zip file:")
        zip_path = input("  Full path: ").strip().strip('"')
        if not os.path.exists(zip_path):
            print("  [ERROR] Still not found: {}".format(zip_path))
            sys.exit(1)

    # Version
    version = input("  Version (e.g. 1.2.0): ").strip()
    if not version:
        print("  [ERROR] Version required.")
        sys.exit(1)

    # Display name
    default_name = "FH6 HeadTracking V{}".format(version)
    display_name = input("  Display name [{}]: ".format(default_name)).strip()
    if not display_name:
        display_name = default_name

    # Changelog
    description = input("  Changelog / description: ").strip()

    # Category
    print("")
    print("  Category: 1=Main  2=Update  3=Optional  4=Old")
    cat_choice = input("  Choose [1]: ").strip() or "1"
    cat_map = {"1": "main", "2": "update", "3": "optional", "4": "old_version"}
    category = cat_map.get(cat_choice, "main")

    # File group ID — hardcoded, no prompt needed
    file_group_id = FILE_GROUP_ID
    print("  File Group ID: {} (hardcoded)".format(file_group_id))

    # Confirm
    print("")
    print("  ─" * 29)
    print("  Ready to upload to nexusmods.com/{}/mods/{}".format(GAME_DOMAIN, MOD_ID))
    print("  File:     {}".format(os.path.basename(zip_path)))
    print("  Version:  {}".format(version))
    print("  Name:     {}".format(display_name))
    print("  Category: {}".format(category))
    print("  Group ID: {}".format(file_group_id))
    print("  ─" * 29)
    print("")
    confirm = input("  Upload now? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        sys.exit(0)

    print("")
    upload_file(api_key, zip_path, file_group_id, version, display_name, description, category)

    print("")
    print("=" * 58)
    print("  Done! Check your mod page:")
    print("  https://www.nexusmods.com/{}/mods/{}".format(GAME_DOMAIN, MOD_ID))
    print("=" * 58)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
