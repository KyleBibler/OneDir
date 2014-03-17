__author__ = 'Student'

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import LoggingEventHandler

class TestEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event.event_type + " file " + event.src_path + " at " + time.asctime())

if __name__ == "__main__":
    event_handler = TestEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='C:\Users\Student\Documents', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()