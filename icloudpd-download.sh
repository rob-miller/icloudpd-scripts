#!/bin/bash

# Path to the decrypted credentials file
CREDENTIALS_FILE="/mnt/ramdisk/decrypted_credentials.txt"

# Check if the decrypted credentials file exists
if [ -f "$CREDENTIALS_FILE" ]; then
    # Source the file to export environment variables
    source "$CREDENTIALS_FILE"
else
    # If the file does not exist, send an email notification and exit
    echo "credentials not decrypted."
    /usr/bin/python3 /usr/local/bin/email-need-decrypt.py
    exit 1
fi

# If the script reaches this point, it means the credentials file exists and has been sourced

/usr/bin/python3 /usr/local/bin/album-download.py

echo "downloading rob iphotos"
# --auto-delete
/usr/local/bin/icloudpd -u $ROB_APPLE_ID --smtp-username $SMTP_ID -p $ROB_APPLE_PASSWD --smtp-password $SMTP_PASSWD --notification-email $SMTP_DEST --cookie-directory $APPLE_AUTH_COOKIE --log-level info --until-found 100 -d /media/nvm1/photos


