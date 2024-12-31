import sys
sys.path.append("third_lib/fastapi")
from typing import Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.chromeService.chromeService import router as chrome_router

app = FastAPI()
# 将编译好的 Vue 项目静态文件夹（如dist）放置在FastAPI项目中的static文件夹下
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(chrome_router, prefix="/api")

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")