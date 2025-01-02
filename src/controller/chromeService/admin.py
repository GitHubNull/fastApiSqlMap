from fastapi import APIRouter, Depends
from model.requestModel.TaskRequest import TaskDeleteRequest
from service.taskService import TaskService
from utils.auth import get_current_user

router = APIRouter(prefix="/chrome/admin")
taskService = TaskService()


@router.post('/task/delete')
async def delete_task(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.delete_task(taskDeleteRequest.taskid)
    return res


@router.post('/task/kill')
async def kill_task(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.kill_task(taskDeleteRequest.taskid)
    return res


@router.get('/task/list')
async def list_task(current_user: dict = Depends(get_current_user)):
    res = await taskService.list_task()
    return res


@router.post('/task/start_with_taskid')
async def start_start_with_taskid(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.start_task_with_taskid(taskDeleteRequest.taskid)
    return res


@router.post('/task/stop')
async def stop_task(taskDeleteRequest: TaskDeleteRequest, current_user: dict = Depends(get_current_user)):
    res = await taskService.stop_task(taskDeleteRequest.taskid)
    return res


@router.post('/task/flush')
async def stop_flush(current_user: dict = Depends(get_current_user)):
    res = await taskService.flush_task()
    return res
