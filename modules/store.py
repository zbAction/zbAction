from threading import Thread

from db import session_factory
from shared import *

class Store(Thread):
    def run(self):
        while 1:
            store_mutex.acquire()
            
            while len(store_queue):
                action = store_queue.pop(0)
                action.save()

            store_mutex.release()