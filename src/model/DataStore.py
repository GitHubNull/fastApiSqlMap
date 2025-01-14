import threading
from collections import OrderedDict
from typing import Optional
from model.Database import Database


# Global data storage
class DataStore(object):
    admin_token: str = ""
    current_db: Optional[Database] = None
    tasks_lock = threading.Lock()
    tasks = OrderedDict()
    username: str = ""
    password: str = ""
    first_checkin_monitor: bool = True
    max_tasks_count: int = 3
    max_tasks_count_lock = threading.Lock()
