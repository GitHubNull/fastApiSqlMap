import pdb
import os

from fastapi import status

from fastapi.exceptions import HTTPException
from model.DataStore import DataStore
# from config import data_store
from model.Task import Task
from model.TaskStatus import TaskStatus
from model.requestModel.TaskRequest import TaskAddRequest
from model.BaseResponseMsg import BaseResponseMsg

from third_lib.sqlmap.lib.core.settings import RESTAPI_UNSUPPORTED_OPTIONS
from third_lib.sqlmap.lib.core.convert import encodeHex
from third_lib.sqlmap.lib.core.data import logger


def validate_options(options):
    if not isinstance(options, dict):
        logger.error("Invalid options format: expected list or tuple")
        return BaseResponseMsg(data=None, msg="Invalid options format", success=False, code=status.HTTP_400_BAD_REQUEST)

    try:
        unsupported_options_set = set(RESTAPI_UNSUPPORTED_OPTIONS)
        for key in options:
            if key in unsupported_options_set:
                logger.warning(f"Unsupported option '{key}' provided to scan_start()")
                return BaseResponseMsg(data=None, msg=f"Unsupported option {key}", success=False, code=status.HTTP_400_BAD_REQUEST)
    except TypeError:
        logger.error("Options is not iterable")
        return BaseResponseMsg(data=None, msg="Options is not iterable", success=False, code=status.HTTP_400_BAD_REQUEST)

    if not options:
        logger.info("No options provided")
        # 根据业务需求决定是否需要返回特定响应
        return BaseResponseMsg(data=None, msg="No options provided", success=True, code=status.HTTP_200_OK)

    return None  # 如果所有选项都支持，则继续后续逻辑


class TaskService(object):
    """
    TaskService
    """
    # def __init__(self, DataStore.current_db, DataStore.tasks_lock, tasks):
    def __init__(self):
        pass
        # DataStore.current_db = DataStore.current_db
        # DataStore.tasks_lock = DataStore.tasks_lock
        # DataStore.tasks = tasks
        # self.dataStore = dataStore

    async def star_task(self, remote_addr: str, scanUrl: str, host, headers: list, body: str, options: dict):
        option_check_res = validate_options(options)
        if option_check_res is not None:
            return option_check_res
        # # 检查是否有不支持的参数
        # for key, value in options:
        #     if key in RESTAPI_UNSUPPORTED_OPTIONS:
        #         logger.warning(f"Unsupported option '{key}' provided to scan_start()")
        #         return BaseResponseMsg(data=None, msg=f"Unsupported option {key}", success=False, code=status.HTTP_400_BAD_REQUEST)

        taskid = encodeHex(os.urandom(8), binary=False)
        try:
            with DataStore.tasks_lock:
                DataStore.tasks[taskid] = Task(taskid, remote_addr, scanUrl, host, headers, body)

                # pdb.set_trace()
                for option in options:
                    logger.debug(f"option: {option}, value: {options[option]}")
                    DataStore.tasks[taskid].set_option(option, options[option])

                # pdb.set_trace()
                # Launch sqlmap engine in a separate process
                DataStore.tasks[taskid].status = TaskStatus.Runnable

            # return {"engineid": DataStore.tasks[taskid].engine_get_id(), "taskid": taskid}
                return BaseResponseMsg(data={"engineid": DataStore.tasks[taskid].engine_get_id(), "taskid": taskid}, msg="success", success=True, code=status.HTTP_200_OK)
        except Exception as e:
            DataStore.tasks[taskid].status = TaskStatus.Terminated
            logger.error("[%s] Failed to start scan: %s" % (taskid, e))
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"{taskid} Non-existing task ID provided to task_delete()")
                return BaseResponseMsg(None, msg="Non-existing task ID", success=False, code=400)
            else:
                status = DataStore.tasks[taskid].status
                if status == TaskStatus.Running:
                    DataStore.tasks[taskid].engine_kill()
                DataStore.tasks.pop(taskid)
                logger.info(f"{taskid} Deleted task")
                return BaseResponseMsg(data=None, msg=f"{taskid} Deleted task", success=True, code=200)

    async def list_task(self):
        tasks = []
        index = 0
        try:
            with DataStore.tasks_lock:
                # pdb.set_trace()
                logger.info(f"id(DataStore.current_db): {id(DataStore.current_db)}")
                if DataStore.current_db is None:
                    logger.error("Database connection is not initialized")
                    # return {"success": False, "message": "Database connection is not initialized"}
                    return BaseResponseMsg(data=None, msg="Database connection is not initialized", success=False, code=500)

                for taskid in DataStore.tasks:
                    task = DataStore.tasks[taskid]
                    errors_query = "SELECT COUNT(*) FROM errors WHERE taskid = ?"
                    cursor = DataStore.current_db.only_execute(
                        errors_query, (taskid,))

                    # pdb.set_trace()
                    if cursor is None:
                        errors_count = 0  # 或者根据需求处理其他逻辑
                    else:
                        errors_count = cursor.fetchone()[0]
                        # errors_count = cursor.fetchone()[0] if cursor.fetchone() is not None else 0
                    # pdb.set_trace()
                    # 获取logs表中特定task_id对应的行数
                    logs_query = "SELECT COUNT(*) FROM logs WHERE taskid = ?"
                    cursor = DataStore.current_db.only_execute(
                        logs_query, (taskid,))
                    if cursor is None:
                        logs_count = 0
                    else:
                        # logs_count = cursor.fetchone()[0] if cursor.fetchone() is not None else 0
                        logs_count = cursor.fetchone()[0]

                    data_query = "SELECT COUNT(*) FROM data WHERE taskid = ?"
                    cursor = DataStore.current_db.only_execute(
                        data_query, (taskid,))
                    if cursor is None:
                        data_count = 0
                    else:
                        data_count = cursor.fetchone()[0]
                        # data_count = cursor.fetchone()[0] if cursor.fetchone() is not None else 0

                    index += 1
                    task_src_status = task.status

                    status = None
                    if task_src_status in [TaskStatus.New, TaskStatus.Runnable, TaskStatus.Blocked]:
                        status = task_src_status.value
                    else:
                        status = TaskStatus.Terminated.value if task.engine_has_terminated(
                        ) is True else TaskStatus.Running.value

                    # pdb.set_trace()
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

            data = {
                "tasks": tasks,
                "tasks_num": len(tasks)
            }
            return BaseResponseMsg(data=data, msg="success", success=True, code=200)
        except Exception as e:
            logger.error(f"Error: {e}")
            return BaseResponseMsg(data=None, msg="error", success=False, code=500)

    async def kill_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"{taskid} Non-existing task ID provided to task_delete()")
                return BaseResponseMsg(data=None, msg="Non-existing task ID", success=False, code=404)
            else:
                status = DataStore.tasks[taskid].status
                if status == TaskStatus.Running:
                    DataStore.tasks[taskid].engine_kill()

                DataStore.tasks[taskid].status = TaskStatus.Terminated
                logger.info(f"[{taskid}] Deleted task")
                # return {"success": True, "message": f"task {taskid} was Killed"}
                return BaseResponseMsg(data=None, msg=f"task {taskid} was Killed", success=True, code=200)

    async def stop_task(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                logger.warning(f"[{taskid}] Invalid task ID provided to scan_stop()")
                return BaseResponseMsg(data=None, success=False, msg=f"task {taskid} was not running", code=status.HTTP_200_OK)
            if DataStore.tasks[taskid].status == TaskStatus.Running:
                DataStore.tasks[taskid].engine_stop()
                DataStore.tasks[taskid].status = TaskStatus.Blocked
                logger.debug(f"[{taskid}] Stopped scan")
                return BaseResponseMsg(data=None, success=True, msg=f"task {taskid} was stopped", code=status.HTTP_200_OK)
            elif DataStore.tasks[taskid].status in [TaskStatus.New, TaskStatus.Runnable]:
                DataStore.tasks[taskid].status = TaskStatus.Blocked
                logger.debug(f"[{taskid}] Stopped scan")
                return BaseResponseMsg(data=None, success=True, msg=f"task {taskid} was stopped", code=status.HTTP_200_OK)
            elif DataStore.tasks[taskid].status == TaskStatus.Blocked:
                logger.warning(f"[{taskid}] task had blocked")
                return BaseResponseMsg(data=None, success=False, msg=f"task {taskid} had blocked", code=status.HTTP_200_OK)
            else:
                logger.warning(f"[{taskid}] task had terminaled!")
                return BaseResponseMsg(data=None, success=False, msg=f"task {taskid} had terminaled", code=status.HTTP_200_OK)

    async def start_task_with_taskid(self, taskid):
        with DataStore.tasks_lock:
            if taskid not in DataStore.tasks:
                raise Exception(f"Task {taskid} does not exist")

            if DataStore.tasks[taskid].status == TaskStatus.Blocked:
                DataStore.tasks[taskid].status = TaskStatus.Runnable
                logger.debug(f"{taskid} Task status changed to Runnable")
                return BaseResponseMsg(data=None, success=True, msg=f"Task status set to {TaskStatus.Runnable}", code=status.HTTP_200_OK)
            else:
                logger.debug(f"{taskid} Task status is {DataStore.tasks[taskid].status}")
                return BaseResponseMsg(data=None, success=False, msg=f"Task status is {DataStore.tasks[taskid].status}", code=status.HTTP_200_OK)

    async def flush_task(self):
        with DataStore.tasks_lock:
            for key in list(DataStore.tasks):
                task = DataStore.tasks[key]
                if task.status == TaskStatus.Running:
                    task.engine_kill()
                del DataStore.tasks[key]

        logger.debug("Flushed task pool")
        return BaseResponseMsg(data=None, msg="Flushed task pool", success=True, code=status.HTTP_200_OK)

    async def find_task_by_urlPath(self, urlPath: str):
        res = []
        with DataStore.tasks_lock:
            for key in list(DataStore.tasks):
                task = DataStore.tasks[key]
                if urlPath in task.scanUrl:
                    res.append(task)

        data = {
            "task": res,
            "count": len(res)
        }
        return BaseResponseMsg(data=data, msg="Find task by urlPath", success=True, code=status.HTTP_200_OK)

    async def find_task_by_taskid(self, taskid: str):
        task = None
        with DataStore.tasks_lock:
            if taskid in DataStore.tasks:
                task = DataStore.tasks[taskid]
            else:
                return None
        data = {
            "task": task
        }
        return BaseResponseMsg(data=data, msg="Find task by taskid", success=True, code=status.HTTP_200_OK)

    async def find_task_by_bodyKeyWord(self, requestBodyKeyWord: str):
        with DataStore.tasks_lock:
            res = []
            for taskid in DataStore.tasks:
                task = DataStore.tasks[taskid]
                if requestBodyKeyWord in task.body:
                    res.append(task)
        data = {
            "data": res,
            "count": len(res),
        }
        return BaseResponseMsg(data=data, msg="success", success=True, code=status.HTTP_200_OK)

    async def find_task_by_header_keyword(self, headerKeyWord: str):
        res = []
        with DataStore.tasks_lock:
            for task in DataStore.tasks.values():
                if task.headers is not None:
                    for k, v in task.headers.items():
                        if headerKeyWord in k or headerKeyWord in v:
                            res.append(task)

        data = {
            "data": res,
            "count": len(res)
        }

        return BaseResponseMsg(data=data, success=True, msg="success", code=status.HTTP_200_OK)

    async def find_task_by_requestHost(self, requestHost: str):
        res = []
        with DataStore.tasks_lock:
            for task in DataStore.tasks.values():
                if task.host == requestHost:
                    res.append(task)

            data = {
                "data": res,
                "count": len(res)
            }
            return BaseResponseMsg(data=data, success=True, msg="success", code=status.HTTP_200_OK)


taskService = TaskService()
