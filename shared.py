from threading import Lock

conn_mutex = Lock()
action_mutex = Lock()
store_mutex = Lock()
store_queue = []
action_queue = []

connections = {}