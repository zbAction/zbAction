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

				del action.receiver

				if receiver.toKey() in connections:
					connections[receiver.toKey()].write_message(
						json.dumps(action.__dict__, default=serialize)
					)

					action.seen = True
				
				store_queue.append(action)

			mutex.release()