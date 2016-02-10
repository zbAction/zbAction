from threading import Thread
import time

from db import session_factory
from secrets import secrets
from shared import *

class Store(Thread):
    def run(self):
        while 1:
            action = store_queue.get()
            action.save()
