from model.Database import Database
from model.DataStore import DataStore
import uvicorn
import sys
sys.path.append("third_lib/APScheduler")
from apscheduler.schedulers.blocking import BlockingScheduler


from utils.task_monitor import monitor


if __name__ == "__main__":
    # Initialize IPC database
    DataStore.current_db = Database()
    DataStore.current_db.connect()
    DataStore.current_db.init()

    scheduler = BlockingScheduler()
    scheduler.add_job(monitor, 'interval', seconds=3)  # 每10秒执行一次
    scheduler.start()
    uvicorn.run("app:app", host="127.0.0.1", port=8775, reload=True)
