# auto_sync
Sync a local and remote folder like Dropbox, via the command line.

# Install

I have truly no idea if this will work cross platform. I only use this on Linux.

To install, you will need the Python package known as 'watchdog' and you'll need the command line tool `rsync`. You can install them like so:

    sudo apt install python-watchdog rsync

After installing dependencies, you can put this file in any folder in your `$PATH` environment variable. Or just copy the file wherever you want to use it. 

## What is this, and why do I want this?

I frequently have a workflow where I want to keep two directories with the same
name on different hosts in sync. I want to be able to keep a script running and
then any changes made in one will sync dropbox style to the folder on the
remote host.

So let's say there's a folder `/home/leland/foo` on my local computer. I'm
going to edit some files in that local folder, and I want those changes to show
up in the folder `/var/bar` on a **remote** computer. And not just in that
directory alone, I want proper sub-directory handling as well. Like this:

    # Sync a local directory and a remote directory. Let's suppose they're both
    # empty for starters.
    auto_sync.py remotehost:/var/bar /home/leland/foo

    # Locally change a file
    touch /home/leland/foo/wow.txt

    # How the directories now look on both machines
    localhost:/home/leland/foo/      remotehost:/var/bar/
    └── wow.txt                      └── wow.txt

    # Make another change, this time a nested local change
    mkdir /home/leland/foo/dang
    touch /home/leland/foo/dang/beta.txt

    # How the directories now look on both machines
    localhost:/home/leland/foo/      remotehost:/var/bar/
    ├── dang                         ├── dang
    │   └── beta.txt                 │   └── beta.txt
    └── wow.txt                      └── wow.txt

This is what `auto_sync.py` does.
