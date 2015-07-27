from datetime import datetime
from user import User

class Action(object):
	attributes = ['event', 'details', 'source', 'receiver']

	def __init__(self, timestamp=datetime.utcnow(), seen=False, **kwargs):
		for attribute in self.attributes:
			setattr(self, attribute, kwargs[attribute])

		self.timestamp = str(timestamp)
		self.seen = seen

	@staticmethod
	def create_from(model):
		if isinstance(model, Action):
			return model

		source = User.create_from(model['source'])
		receiver = User.create_from(model['receiver'])

		return Action(event=model['event'], details=model['details'], source=source, receiver=receiver)