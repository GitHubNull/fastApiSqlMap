from pydantic import BaseModel, Field
from typing import Annotated, Optional


class TaskAddRequest(BaseModel):
    # taskid: Annotated[Optional[str], Field(description="任务ID，可选参数")]
    options: Annotated[dict, Field(min_length=1, description="参数列表")]


class TaskDeleteRequest(BaseModel):
    taskid: str


class TaskUpdateRequest(BaseModel):
    taskid: Annotated[str, Field(min_length=1)]
    options: Annotated[dict, Field(min_length=1)]


class TaskListRequest(BaseModel):
    pass


class TaskQueryRequest(BaseModel):
    taskid: Annotated[Optional[str], Field(description="任务ID，可选参数")]
