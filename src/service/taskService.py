import os
import json

from model.DataStore import DataStore
from model.Database import Database
from model.Task import Task
from model.TaskStatus import TaskStatus
from model.requestModel.TaskRequest import TaskAddRequest
from sqlmap.lib.core.settings import RESTAPI_UNSUPPORTED_OPTIONS
from third_lib.sqlmap.lib.core.convert import encodeHex
from third_lib.sqlmap.lib.core.data import logger


class TaskService(object):
    """
    TaskService
    """
    def __init__(self):
        pass
        # DataStore = DataStore

    async def star_task(self, remote_addr: str, taskAddRequest: TaskAddRequest):
        options = taskAddRequest.options

        if options is None:
            logger.error("Options is empty")
            return {"success": False, "message": "Options is empty"}

        # 检查是否有不支持的参数
        for key, value in options:
            if key in RESTAPI_UNSUPPORTED_OPTIONS:
                logger.warning(f"Unsupported option '{key}' provided to scan_start()")
                return {"success": False, f"message": f"Unsupported option {key}"}

        taskid = encodeHex(os.urandom(8), binary=False)

        with DataStore.tasks_lock:
            DataStore.tasks[taskid] = Task(taskid, remote_addr)

            for option, value in options:
                DataStore.tasks[taskid].set_option(option, value)

            # Launch sqlmap engine in a separate process
            DataStore.tasks[taskid].status = TaskStatus.Runnable

    async def delete_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"{taskid} Non-existing task ID provided to task_delete()")
                return {"success": False, "message": "Non-existing task ID"}
            else:
                status = DataStore.tasks[taskid].status
                if status == TaskStatus.Running:
                    DataStore.tasks[taskid].engine_kill()
                DataStore.tasks.pop(taskid)
                logger.info(f"{taskid} Deleted task")
                return {"success": True, "message": f"{taskid} Deleted task"}

    async def list_task(self):
        tasks = []
        index = 0
        with DataStore.tasks_lock:
            if DataStore.current_db is None:
                logger.error("Database connection is not initialized")
                return {"success": False, "message": "Database connection is not initialized"}

            for taskid in DataStore.tasks:
                task = DataStore.tasks[taskid]
                errors_query = "SELECT COUNT(*) FROM errors WHERE taskid = ?"
                cursor = DataStore.current_db.only_execute(
                    errors_query, (taskid,))
                if cursor is None:
                    errors_count = 0  # 或者根据需求处理其他逻辑
                else:
                    errors_count = cursor.fetchone()[0] if cursor.fetchone() else 0

                # 获取logs表中特定task_id对应的行数
                logs_query = "SELECT COUNT(*) FROM logs WHERE taskid = ?"
                cursor = DataStore.current_db.only_execute(
                    logs_query, (taskid,))
                if cursor is None:
                    logs_count = 0
                else:
                    logs_count = cursor.fetchone()[0] if cursor.fetchone() else 0

                data_query = "SELECT COUNT(*) FROM data WHERE taskid = ?"
                cursor = DataStore.current_db.only_execute(
                    data_query, (taskid,))
                if cursor is None:
                    data_count = 0
                else:
                    data_count = cursor.fetchone()[0] if cursor.fetchone() else 0

                index += 1
                task_src_status = task.status

                status = None
                if task_src_status in [TaskStatus.New, TaskStatus.Runnable, TaskStatus.Blocked]:
                    status = task_src_status.value
                else:
                    status = TaskStatus.Terminated.value if task.engine_has_terminated(
                    ) is True else TaskStatus.Running.value

                resul_task_item = {
                    "index": index,
                    "start_datetime": None if task.start_datetime is None else task.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "task_id": taskid,
                    "errors": errors_count,
                    "logs": logs_count,
                    "status": status,
                    "injected": data_count > 0
                }
                tasks.append(resul_task_item)

        return {"success": True, "message": "success", "tasks": tasks, "tasks_num": len(tasks)}

    async def kill_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"{taskid} Non-existing task ID provided to task_delete()")
                return {"success": False, "message": "Non-existing task ID"}
            else:
                status = DataStore.tasks[taskid].status
                if status == TaskStatus.Running:
                    DataStore.tasks[taskid].engine_kill()

                DataStore.tasks[taskid].status = TaskStatus.Terminated
                logger.info(f"[{taskid}] Deleted task")
                return {"success": True, "message": f"task {taskid} was Killed"}

    async def stop_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"[{taskid}] Invalid task ID provided to scan_stop()")
                return {"success": False, "message": "Invalid task ID"}
            if DataStore.tasks[taskid].status == TaskStatus.Running:
                DataStore.tasks[taskid].engine_stop()
                DataStore.tasks[taskid].status = TaskStatus.Blocked
                logger.debug(f"[{taskid}] Stopped scan")
                return {"success": True}
            elif DataStore.tasks[taskid].status in [TaskStatus.New, TaskStatus.Runnable]:
                DataStore.tasks[taskid].status = TaskStatus.Blocked
                logger.debug(f"[{taskid}] Stopped scan")
                return {"success": True}
            elif DataStore.tasks[taskid].status == TaskStatus.Blocked:
                logger.warning(f"[{taskid}] task had blocked")
                return {"success": False, "message": "Task had blocked!"}
            else:
                logger.warning(f"[{taskid}] task had terminaled!")
                return {"success": False, "message": "Task had terminaled!"}

    async def start_task_with_taskid(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                raise Exception(f"Task {taskid} does not exist")

            if DataStore.tasks[taskid].status == TaskStatus.Blocked:
                DataStore.tasks[taskid].status = TaskStatus.Runnable
                logger.debug(f"{taskid} Task status changed to Runnable")
                return {"success": True, "message": f"Task status set to {TaskStatus.Runnable}"}
            else:
                logger.debug(f"{taskid} Task status is {DataStore.tasks[taskid].status}")
                return {"success": False, "message": f"Task status is {DataStore.tasks[taskid].status}"}

    async def flush_task(self):
        with DataStore.tasks_lock:
            for key in list(DataStore.tasks):
                task = DataStore.tasks[key]
                if task.status == TaskStatus.Running:
                    task.engine_kill()
                del DataStore.tasks[key]

        logger.debug("Flushed task pool")
        return {"success": True}
