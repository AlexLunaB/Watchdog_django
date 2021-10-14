import os


import logging
import queue
import threading
import time
import watchdog.observers as observers
import watchdog.events as events
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchDjango.settings")

SENTINEL = None


def upload(f, remote_path, local_path):
    fp = open(local_path, "rb")
    buf_size = 1024
    f.storbinary("STOR {}".format(remote_path), fp, buf_size)
    fp.close()


class MyEventHandler(events.FileSystemEventHandler):
    def on_any_event(self, event):
        super(MyEventHandler, self).on_any_event(event)
        queue.put(event)

    def __init__(self, queue):
        self.queue = queue


def process(queue):
    while True:
        event = queue.get()
        logger.info(event)
        print(event.key)  # tuple

        if (event.key)[0] == "created":
            fp = open(event.src_path, "rb")

            print(os.path.getsize(event.src_path))
            print(os.path.getmtime(event.src_path))
            print(os.path.getctime(event.src_path))
            channel_layer = get_channel_layer()
            try:
                async_to_sync(channel_layer.group_send)(
                    "files",
                    {
                        'type': 'send_message',
                        'message': str(event.src_path)
                    }
                )
            except ValueError:
                pass
            print("mensaje enviado")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(threadName)s] %(message)s',
                        datefmt='%H:%M:%S')
    queue = queue.Queue()
    num_workers = 4
    pool = [threading.Thread(target=process, args=(queue,)) for i in range(num_workers)]
    for t in pool:
        t.daemon = True
        t.start()

    event_handler = MyEventHandler(queue)
    observer = observers.Observer()
    observer.schedule(
        event_handler,
        path=r'C:\Users\USUARIO\Documents\watchDjango',
        recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()