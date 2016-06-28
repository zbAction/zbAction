import os
import json

from object import Object

secrets = Object()

path = os.path.abspath(os.path.join('/zba', 'secrets.json'))

with open(path) as f:
    lines = ''.join(f.readlines())

    s = json.loads(lines)

    secrets.update(s)

del path
