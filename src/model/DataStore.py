import threading


# Global data storage
class DataStore(object):
    tasks_lock = threading.Lock()
    admin_token = ""
    current_db = None
    tasks = dict()
    username = None
    password = None