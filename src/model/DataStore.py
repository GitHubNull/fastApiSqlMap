import threading
from collections import OrderedDict
from typing import Optional
from model.Database import Database


# Global data storage
class DataStore(object):
    admin_token = ""
    current_db: Optional[Database] = None
    tasks_lock = threading.Lock()
    tasks = OrderedDict()
    username = None
    password = None
