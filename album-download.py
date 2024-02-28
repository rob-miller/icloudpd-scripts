#!/usr/bin/python3
"""album-download.py.

This script runs icloudpd photo downloader for a list of users.  Apple
credentials, smtp credentials and the location of the pre-configured Apple
auth cookies (see icloudpd documentation) must be available as environment
variables.

For each user, the list of available albums is retrieved.  Each album not in
`ignore_albums` is downloaded to `base_output_dir`.

The program sleeps for `main_delay` seconds after each album download.

Usage:
    python script_name.py [-l]

Arguments:
    -l    list directories only, do not download (checks credentials)

"""
from dotenv import load_dotenv
import subprocess
import os
import time
import sys
import argparse

load_dotenv()

# Configuration
icloudpd_path = "/usr/local/bin/icloudpd"

username = None  # os.getenv('JANE_APPLE_ID')
password = None  # os.getenv('JANE_APPLE_PASSWD')

base_output_dir = None  # "/media/nvm1/photos/albums/jane"

cookie_dir = os.getenv('APPLE_AUTH_COOKIE')

smtp_username = os.getenv('SMTP_ID')
smtp_password = os.getenv('SMTP_PASSWD')

smtp_sendto = os.getenv('SMTP_DEST')

main_delay = 190

ignore_albums = [
    "All Photos",
    "Time-lapse",
    "Videos",
    "Slo-mo",
    "Bursts",
    "Favorites",
    "Panoramas",
    "Screenshots",
    "Live",
    "Recently Deleted",
    "Hidden",
    # Jane
    "Instagram",
    "Twitter",
    # rob
    "You Doodle Pro",
    "WhatsApp",
    "Scannable",
    "Dropbox",
    "RAW",
    "Fjorden",
    "Canon EOS R7"
]

# Set up command-line argument parsing for dry-run option
parser = argparse.ArgumentParser(description='Download icloud photo albums.')
parser.add_argument('-l', action='store_true', help='Only list albums.')
args = parser.parse_args()

# Set global dry_run variable and dry_run_prefix for logging
list_only = args.l


def list_albums():
    command = [
        icloudpd_path,
        "-u", username,
        "--smtp-username", smtp_username,
        "-l",
        "--notification-email", smtp_sendto,
        "-p", password,
        "--smtp-password", smtp_password,
        "--cookie-directory", cookie_dir,
        "--log-level", "error"
    ]
    # print(command)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout
    else:
        print(result.stdout)
        print(result.stderr)
        raise Exception("Failed to list albums")


def download_album(album_name):
    album_dir = os.path.join(base_output_dir, album_name)
    if not os.path.exists(album_dir):
        os.makedirs(album_dir)
    command = [
        icloudpd_path,
        "-u", username,
        "--smtp-username", smtp_username,
        "--notification-email", smtp_sendto,
        "-p", password,
        "--smtp-password", smtp_password,
        "--log-level", "error",
        "--no-progress-bar",
        "--cookie-directory", cookie_dir,
        # "--only-print-filenames",
        "--folder-structure", "none",
        "-a", album_name,
        "-d", album_dir
    ]
    result = subprocess.run(command)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise Exception(f"Failed to download album {album_name}")


def main():
    print("starting album-download.py")
    for targ in ["jane", "rob"]:
        global username, password, base_output_dir

        if targ == "jane":
            username = os.getenv('JANE_APPLE_ID')
            password = os.getenv('JANE_APPLE_PASSWD')

            base_output_dir = "/media/nvm1/photos/albums/jane"
        elif targ == "rob":
            username = os.getenv('ROB_APPLE_ID')
            password = os.getenv('ROB_APPLE_PASSWD')

            base_output_dir = "/media/nvm1/photos/albums/rob"           

        print(f"downloading iphoto albums for user {targ}")
        albums_output = list_albums()
        if list_only:
            print(albums_output)
        else:
            time.sleep(10)
            albums = [line.strip() for line in albums_output.split("\n") if line.strip() and "Albums:" not in line]
            for album in albums:
                if album not in ignore_albums:
                    print(f"Downloading album: {album} for user {targ}")
                    try:
                        download_album(album)
                    except Exception as e:
                        print(f"error downloading album {album} for user {targ}:")
                        print(e)
                        print(f"exit in {main_delay} seconds")
                        time.sleep(main_delay)
                        sys.exit(1)
                    time.sleep(main_delay)
                else:
                    print(f"Ignoring album: {album}")


if __name__ == "__main__":
    main()
