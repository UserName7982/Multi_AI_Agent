from src.DB.postgres import PoolManager
from ..taskscheduling.celery import app
from ..taskscheduling.handle_task import handle_task
from ..config import config

@app.task(name="task.execute_task")
def execute_task(task_id):
    (handle_task(task_id))
