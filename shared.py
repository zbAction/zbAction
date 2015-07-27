from threading import Lock

mutex = Lock()
store_queue = []
action_queue = []

connections = {}