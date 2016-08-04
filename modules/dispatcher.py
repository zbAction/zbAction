import json
from threading import Thread
import time

from helpers import serialize
from logger import log
from secrets import secrets
from shared import *
from models.user import User

class Dispatcher(Thread):
    def run(self):
        while 1:
            action = action_queue.get()
            receiver = User.from_access_key(action.receiver)

            data = {
                'id': action.id,
                'timestamp': str(action.timestamp),
                'event': action.event,
                'details': action.details,
                'source': User.from_access_key(action.source).to_json(),
                'seen': action.seen
            }

            seen = False

            for conn in connections:
                if conn[0] == receiver.toKey():
                    log('Sending', json.dumps(data))

                    conn[1].write_message(
                        json.dumps(data)
                    )

                    seen = True

            action.seen = seen
            store_queue.put(action)
