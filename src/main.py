import uvicorn
import sys
sys.path.append("third_lib/APScheduler")
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=3)  # 每10秒执行一次
    scheduler.start()
    uvicorn.run("app:app", host="127.0.0.1", port=8775, reload=True)