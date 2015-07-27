from user import User

def serialize(var):
	if isinstance(var, User):
		return var.to_json()

	if isinstance(var, object):
		return var.__dict__
	else:
		return var