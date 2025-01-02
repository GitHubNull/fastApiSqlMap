from config import MAX_TASKS_COUNT, MAX_TASKS_COUNT_LOCK
from model.DataStore import DataStore


def monitor(max_tasks_count=None):
    local_max_tasks_count = 0
    with MAX_TASKS_COUNT_LOCK:
        if max_tasks_count is not None and max_tasks_count > 0 and max_tasks_count > MAX_TASKS_COUNT:
            local_max_tasks_count = MAX_TASKS_COUNT
        else:
            local_max_tasks_count = max_tasks_count

    with DataStore.tasks_lock:
        runnable_list = []
        running_task_cnt = 0

        for taskid in DataStore.tasks:
            task = DataStore.tasks[taskid]
            task_orin_status = task.status
