import json
from threading import Thread

from shared import *

from helpers import serialize

class Dispatcher(Thread):
	def run(self):
		while 1:
			mutex.acquire()
			while len(action_queue):
				action = action_queue.pop(0)
				receiver = action.receiver

				if receiver.toKey() in connections:
					# Delete receiver so we don't send
					# the receiver to the receiver.
					# Will be restored before storing.
					del action.receiver

					connections[receiver.toKey()].write_message(
						json.dumps(action.__dict__, default=serialize)
					)

					action.seen = True
				else:
					action_queue.append(action)

				# Note to self: need to check fo row
				# with the exact same columns to avoid
				# duplicates (do this inside store.py)
				setattr(action, 'receiver', receiver)
				store_queue.append(action)				

			mutex.release()