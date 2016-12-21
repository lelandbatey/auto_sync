#!/usr/bin/env python2

'''
auto_sync.py

It's like dropbox syncing two folders.

Pass in a remote path and a local path. For example:

    auto_sync.py example.com:/foo/bar/ ./bang
'''

from __future__ import print_function

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print("`Watchdog` module is not installed.")
from Queue import Queue, Empty
from threading import Thread
import time
import sys
import os

REMOTE_HOST_PATH = ''
LOCAL_PATH = ''
PATH_QUEUE = Queue()


def build_command(path):
    """Builds the str for the shell command to upload files."""
    global LOCAL_PATH
    cmd_str = ['rsync -az']
    path = os.path.abspath(path)
    remote = os.path.normpath(REMOTE_HOST_PATH + path.replace(LOCAL_PATH, ""))

    cmd_str.append('"' + path + '"')
    cmd_str.append('"' + remote + '"')
    return ' '.join(cmd_str)


class RunCommands(Thread):
    """Forever attempts to upload files in input queue."""

    def __init__(self, cmd_queue):
        super(RunCommands, self).__init__()
        self.cmd_queue = cmd_queue

    def run(self):
        """Tries to upload files in queue. If the queue is empty, the thread
        sleeps for 0.5 seconds then tries to read again."""
        while True:
            try:
                path = self.cmd_queue.get_nowait()
                if path:
                    # Do this so something can shut down this thread externally.
                    if path == 'END_PROCESS': break
                    cmd = build_command(path)
                    print(cmd)
                    os.system(cmd)
            except Empty:
                time.sleep(0.5)
        return

    def stop(self):
        """Cause the `run` method to exit."""
        self.cmd_queue.put('END_PROCESS')
        return


class FileUploader(FileSystemEventHandler):
    """Handles the uploading of files when a change is detected."""

    #pylint: disable=R0201
    def on_modified(self, event):
        """Overrides the on_modified method."""
        print("File modified", event.src_path)
        PATH_QUEUE.put(event.src_path)

    def on_created(self, event):
        """Prints path of newly created file."""
        print("File created", event.src_path)


def main():
    """Initializes our watchdog setup."""
    global REMOTE_HOST_PATH
    global LOCAL_PATH
    if len(sys.argv) > 1:
        REMOTE_HOST_PATH = sys.argv[1]
        LOCAL_PATH = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
        LOCAL_PATH = os.path.abspath(LOCAL_PATH)
    else:
        helptxt = """
Please provide a remote host as first argument and a local path as the second
argument. If no local path is provided, then the current directory is used.

For example:

    # sync changes to the local path into the remote path
    {} example.com:/foo/bar/ ./bang/
        """
        print(helptxt.format(sys.argv[0]))
        exit()

    event_handler = FileUploader()
    observer = Observer()
    observer.schedule(event_handler, path=LOCAL_PATH, recursive=True)
    observer.start()

    # Here we create the thread to constantly attempt to upload modified files.
    upload_thread = RunCommands(PATH_QUEUE)
    upload_thread.daemon = True
    upload_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        upload_thread.stop()
    observer.join()
    upload_thread.join()


if __name__ == '__main__':
    main()
