from fastapi import APIRouter, Depends, Query
from model.requestModel.TaskRequest import TaskDeleteRequest, TaskFindByBodyKeyWordRequest, TaskFindByHeaderKeyWordRequest, TaskFindByUrlPathRequest, TaskStopRequest
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


# 创建 Pydantic 模型来定义查询参数的结构
class ItemQuery(BaseModel):
    q: str = Field("", min_length=3, max_length=50)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


@router.get("/items/")
async def read_items(item_query: ItemQuery = Depends()):
    return {"message": "Hello World", "params": item_query.dict()}