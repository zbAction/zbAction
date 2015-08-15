from Queue import Queue
import os
from threading import Lock

conn_mutex = Lock()
store_queue = Queue()
action_queue = Queue()

connections = []

base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))

own_regex = lambda x: "<script>\s*window\.__zbAction\s*=\s*{\s*board_key\s*:\s*'" + x + "'\s*}\s*;\s*</script>"
