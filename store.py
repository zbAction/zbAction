from threading import Thread

from shared import *

class Store(Thread):
	def run(self):
		while 1:
			mutex.acquire()
			
			while len(store_queue):
				# dequeue and insert into db
				break

			mutex.release()