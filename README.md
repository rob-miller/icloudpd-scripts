# icloudpd-scripts

[icloud-photos-downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader) is a great tool
that I want to run regularly to maintain local copies of my iPhone photos and all the albums my wife and I create
-- including new albums without having to do anything.


The system shown here uses environment variables for passwords and not the Python keyring library of icloudpd.  My credentials
are 'encrypted at rest', only root has access to them while the system is running, and I run one command with one password 
from my main computer to unlock the system once it boots.  The scripts run as root, leaving root as the owner of all the
photos on the drive.

You are welcome to use these scripts for your own purposes, you will of course have to edit them lightly for your
own environment and user names.  

## album-download.py

This script downloads albums for my wife and myself.  It gets the list of albums from iCloud, then downloads those that
are not on an ignore list (so new albums are downloaded by default).  It sleeps for a few minutes after each album
download as I think Apple closes the connection if you download too many photos at once.  If run with `-l` parameter it
will only list the albums from each account, so this is a good way to test if your credentials are set up correctly.

## icloudpd-download.sh

This bash script reads the decrypted credentials file to set the environment variables, then runs `album-download.py`
followed by a direct call to `icloudpd` to download all my recent photos.  If the decrypted credentials file is not
available, this runs `email-need-decrypt.py` to ask for help.

## email-need-decrypt.py

Python script to send an email, unfortunately using hardcoded SMTP credentials (because the decrypted file is not
accessible).  Use a throwaway Gmail account.

## icloudpd-rtm.timer
## icloudpd-rtm.service

These files work in /etc/systemd/system to run `icloudpd-download.sh` nightly at 5:00 AM GMT.  Once installed, they need

     `systemctl daemon-reload`
     `systemctl enable icloudpd-rtm.timer`
     `systemctl start icloudpd-rtm.timer`

## credentials.txt

This file stores the Apple and SMTP (Google) credentials for calling icloudpd.  Use the syntax as shown, executing it
with `bash` will export the environment variables.

Proceed as follows to set up the encrypted credentials:

1.  Create a ramdisk by adding this line to /etc/fstab:

    ramfs /mnt/ramdisk ramfs defaults 0 0

2. Make the ramdisk only accessible to root by creating 

    /etc/systemd/system/setramfsperms.service

containing:

    [Unit]
    Description=Set Permissions for /mnt/ramdisk
    Requires=local-fs.target
    After=local-fs.target

    [Service]
    Type=oneshot
    ExecStart=/bin/chmod 700 /mnt/ramdisk
    ExecStart=/bin/chown root:root /mnt/ramdisk
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target

3. Enable `setramfsperms.service` with 

    systemctl enable setramfsperms.service

on reboot you should have /mnt/ramdisk readable only by root

4.  create `credentials.txt` file to export environment variables for user ids and passwords
as shown in the example file.  Place this file in /root/.

encrypt this file with

    gpg --symmetric --cipher-algo AES256 credentials.txt


5. Create as your normal user (`<yourLogin>`) a bash script `bin/decrypt-icloudpd.sh` to decrypt and place on ramdisk:

    #!/usr/bin/bash
    gpg --decrypt --output /mnt/ramdisk/decrypted_credentials.txt /root/icloudpd-credentials.txt.gpg

6.  Add this command for <yourLogin> to `sudoers` using the NOPASSWD option with `visudo`:

    <yourLogin> ALL=(ALL) NOPASSWD: /home/<yourLogin>/bin/decrypt-icloudpd.sh


At this point you should be able to remote execute from ssh with 

    ssh -t i7-0 sudo bin/decrypt-icloudpd.sh

and only need to supply the gpg passphrase (search online for how to configure passwordless ssh logins).

Test the credentials setup with 

    source /mnt/ramdisk/decrypted_credentials.txt
    album-download.py -l

and the album lists for your users should be printed.

If everything has worked, go back and _delete_ your unencrypted `credentials.txt` file.

After the timer has triggered, you can check the messages from `icloudpd-rtm.service` with

    sudo journalctl -u icloudpd-rtm

You can execute the icloudpd-rtm service without waiting for the timer with:

    sudo systemctl start icloudpd-rtm.service



