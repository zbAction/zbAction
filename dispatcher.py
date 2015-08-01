import json
from threading import Thread

from shared import *

from helpers import serialize
from user import User

class Dispatcher(Thread):
	def run(self):
		while 1:
			action_mutex.acquire()

			while len(action_queue):
				action = action_queue.pop(0)
				receiver = User.from_id(action.receiver)

				if receiver.toKey() in connections:
					data = {
						'timestamp': str(action.timestamp),
						'event': action.event,
						'details': action.details,
						'source': User.from_id(action.source).to_json(),
						'seen': action.seen
					}

					connections[receiver.toKey()].write_message(
						json.dumps(data)
					)

					action.seen = True

				store_mutex.acquire()
				store_queue.append(action)
				store_mutex.release()

			action_mutex.release()