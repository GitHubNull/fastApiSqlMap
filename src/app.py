# import sys
# sys.path.append("third_lib/fastapi")
from typing import Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from third_lib.sqlmap.lib.core.data import logger

from controller.chromeService.admin import router as chrome_admin_router

app = FastAPI()
# 将编译好的 Vue 项目静态文件夹（如dist）放置在FastAPI项目中的static文件夹下
app.mount("/static", StaticFiles(directory="static"), name="static")
# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    # 允许所有来源，你也可以设置为具体的域名来限制请求来源，例如 ["https://example.com"]
    allow_origins=["http://127.0.0.1:5173", 
                   "http://127.0.0.1:8775", 
                   "http://localhost:5173"],
    allow_credentials=True,  # 允许携带身份凭证，如cookies
    allow_methods=["*"],   # 允许所有HTTP方法
    allow_headers=["*"]    # 允许所有请求头
)

app.include_router(chrome_admin_router, prefix="/api")


@app.get("/")
def read_root():
    logger.debug("root")
    return RedirectResponse(url="/static/index.html")