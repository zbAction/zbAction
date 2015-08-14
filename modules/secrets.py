import os
import json

class secret:
    pass

def parse_val(var):
    if isinstance(var, dict):
        placeholder = secret()

        for key in var:
            if isinstance(var[key], dict):
                setattr(placeholder, key, parse_val(var[key]))
            elif isinstance(var[key], list):
                setattr(placeholder, key, [])

                for x in var[key]:
                    placeholder[key].push(parse_val(x))
            else:
                setattr(placeholder, key, var[key])

        return placeholder

    return var

secrets = secret()

path = os.path.abspath(os.path.join('/zba', 'secrets.json'))

with open(path) as f:
    lines = ''.join(f.readlines())

    s = json.loads(lines)

    for key in s:
        setattr(secrets, key, parse_val(s[key]))

del secret
del parse_val
del path
