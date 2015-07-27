import os
import json

class secret:
	def __str__(self):
		return json.dumps(self.__dict__)

def parse_val(var):
	if isinstance(var, dict):
		placeholder = secret()

		for key in var:
			setattr(placeholder, key, var[key])

		return placeholder

	return var

secrets = secret()

path = os.path.abspath(
	os.path.join(os.path.dirname(__file__), '..', 'secrets.json')
)

with open(path) as f:
	lines = ''.join(f.readlines())

	s = json.loads(lines)

	for key in s:
		setattr(secrets, key, parse_val(s[key]))

del secret
del parse_val
del path