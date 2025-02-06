from datetime import datetime
import random
from fastapi import APIRouter, Depends, Query
from model.BaseResponseMsg import BaseResponseMsg
from model.requestModel.TaskRequest import TaskDeleteRequest, TaskFindByBodyKeyWordRequest, TaskFindByHeaderKeyWordRequest, TaskFindByUrlPathRequest, TaskLogQueryRequest, TaskStopRequest
from pydantic import BaseModel, Field
from typing import Optional
from service.taskService import taskService
from utils.auth import get_current_user
from third_lib.sqlmap.lib.core.data import logger

router = APIRouter(prefix="/chrome/admin")
# taskService = TaskService()


@router.delete('/task/delete')
async def delete_task(taskDeleteRequest: TaskDeleteRequest = Depends(), current_user: dict = Depends(get_current_user)):
    res = await taskService.delete_task(taskDeleteRequest.taskid)
    return res


@router.put('/task/kill')
async def kill_task(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.kill_task(taskDeleteRequest.taskid)
    return res


@router.get('/task/list')
async def list_task(current_user: dict = Depends(get_current_user)):
    res = await taskService.list_task()
    return res


@router.put('/task/startBlocked')
async def start_start_with_taskid(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.start_task_with_taskid(taskDeleteRequest.taskid)
    return res


@router.put('/task/stop')
async def stop_task(taskStopRequest: TaskStopRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.stop_task(taskStopRequest.taskid)
    return res


@router.patch('/task/flush')
async def stop_flush(current_user: dict = Depends(get_current_user)):
    res = await taskService.flush_task()
    return res


@router.post('/task/findByUrlPath')
async def find_task_by_urlPath(taskFindByUrlPathRequest: TaskFindByUrlPathRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.find_task_by_urlPath(taskFindByUrlPathRequest.urlPath)
    return res


@router.post('/task/findByBodyKeyWord')
async def find_task_by_bodyKeyWord(taskFindByBodyKeyWordRequest: TaskFindByBodyKeyWordRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.find_task_by_bodyKeyWord(taskFindByBodyKeyWordRequest.bodyKeyWord)
    return res


@router.post('/task/findByHeaderKeyWord')
async def find_task_by_headerKeyWord(taskFindByHeaderKeyWordRequest: TaskFindByHeaderKeyWordRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.find_task_by_header_keyword(taskFindByHeaderKeyWordRequest.headerKeyWord)
    return res


@router.get('/task/logs/getLogsByTaskId')
async def get_logs_by_taskid(taskLogQueryRequest: TaskLogQueryRequest = Depends(), current_user: dict = Depends(get_current_user)):
    res = await taskService.find_task_log_by_taskid(taskid=taskLogQueryRequest.taskId)
    return res

    # test data

    # 初始化日志列表
    # json_log_messages = []

    # # 定义日志级别集合
    # level_set = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    # # 定义一些 SQLMap 日志相关的关键词和模板
    # injection_types = [
    #     "Boolean-based blind SQL injection",
    #     "Error-based SQL injection",
    #     "Time-based SQL injection",
    #     "Union query SQL injection",
    #     "Stacked queries injection"
    # ]

    # parameters = [
    #     "id", "username", "password", "search", "category", "product_id"
    # ]

    # urls = [
    #     "http://example.com/login",
    #     "http://testphp.vulnweb.com/search.php",
    #     "http://vulnerable-site.com/products",
    #     "http://inject.me/user/login",
    #     "http://192.168.1.100/admin/form.php"
    # ]

    # # 定义一些常见的 SQLMap 日志模板
    # log_templates = [
    #     "[INFO] Testing for SQL injection on GET parameter '{param}'",
    #     "[DEBUG] Using payload: {payload}",
    #     "[WARNING] {injection_type} detected",
    #     "[ERROR] Connection timeout for {url}",
    #     "[CRITICAL] Failed to retrieve database schema",
    #     "[DEBUG] Cleaning up configuration parameters",
    #     "[INFO] Loading tamper script '{tamper_script}'",
    #     "[WARNING] Heuristic (parsing) test showed that the back-end DBMS could be '{dbms}'",
    #     "[ERROR] Network error for {url}"
    # ]

    # # 定义一些常见的 SQLMap payload 和其他内容
    # payloads = [
    #     "' OR 1=1--",
    #     "' UNION SELECT 1, 2, 3--",
    #     "' AND SLEEP(5)--",
    #     "' OR '1'='1",
    #     "' UNION ALL SELECT NULL, @@version--"
    # ]

    # tamper_scripts = [
    #     "randomcase.py",
    #     "space2comment.py",
    #     "between.py",
    #     "utf8mb4.py"
    # ]

    # databases = [
    #     "MySQL",
    #     "PostgreSQL",
    #     "Microsoft SQL Server",
    #     "Oracle",
    #     "SQLite"
    # ]

    # # 生成 200 条日志
    # for i in range(200):
    #     template = random.choice(log_templates)
    #     if "payload" in template:
    #         payload = random.choice(payloads)
    #         template = template.format(payload=payload)
    #     if "param" in template:
    #         param = random.choice(parameters)
    #         template = template.format(param=param)
    #     if "url" in template:
    #         url = random.choice(urls)
    #         template = template.format(url=url)
    #     if "injection_type" in template:
    #         injection_type = random.choice(injection_types)
    #         template = template.format(injection_type=injection_type)
    #     if "tamper_script" in template:
    #         tamper_script = random.choice(tamper_scripts)
    #         template = template.format(tamper_script=tamper_script)
    #     if "dbms" in template:
    #         dbms = random.choice(databases)
    #         template = template.format(dbms=dbms)

    #     json_log_messages.append({
    #         'level': random.choice(level_set),
    #         'message': template,
    #         'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     })

    # return BaseResponseMsg(data=json_log_messages, msg="success", success=True, code=200)


# 创建 Pydantic 模型来定义查询参数的结构
class ItemQuery(BaseModel):
    q: str = Field("", min_length=3, max_length=50)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


@router.get("/items/")
async def read_items(item_query: ItemQuery = Depends()):
    return {"message": "Hello World", "params": item_query.dict()}