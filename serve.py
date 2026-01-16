#!/usr/bin/env python
import os
import subprocess
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarkdownChangeHandler(FileSystemEventHandler):
    def __init__(self, debounce_time=1.0):
        super().__init__()
        self.restart_required = False
        self.debounce_time = debounce_time
        self._last_trigger_time = 0
        self.relevant_events = (FileModifiedEvent, FileCreatedEvent, FileDeletedEvent)

    def on_any_event(self, event):
        if event.is_directory or not isinstance(event, self.relevant_events):
            return
        if event.src_path.endswith('.md'):
            current_time = time.time()
            if (current_time - self._last_trigger_time) > self.debounce_time:
                logger.info(f"📝 Change Detected: {event.src_path}")
                self.restart_required = True
                self._last_trigger_time = current_time

def run_serve():
    return subprocess.Popen(["uv", "run", "mkdocs", "serve"], stdout=sys.stdout, stderr=sys.stderr)

def main():
    mkdocs_process = run_serve()
    event_handler = MarkdownChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.getcwd(), recursive=True)
    observer.start()

    try:
        while True:
            if event_handler.restart_required:
                logger.warning("Restarting MkDocs...")
                mkdocs_process.terminate()
                mkdocs_process.wait()
                mkdocs_process = run_serve()
                event_handler.restart_required = False
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        mkdocs_process.terminate()
        observer.join()

if __name__ == "__main__":
    main()
