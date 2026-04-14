from datetime import datetime
from ..taskscheduling.handle_task import handle_task
from ..taskscheduling.services import update_tasks_feild
from celery import shared_task
from Logger import logger
@shared_task(max_retries=3,name="task.execute_task",bind=True)
def execute_task(self,task_id):
    update_tasks_feild(task_id,status="running")
    try:
        handle_task(task_id)
        update_tasks_feild(task_id,status="completed",completed_at=datetime.utcnow())
    except Exception as e:
        retries=self.request.retries
        if retries > 3:
            logger.error(f"Task with ID {task_id} failed after {retries} retries: {e}")
            update_tasks_feild(task_id,status="failed")
        else:
            logger.error(f"Task with ID {task_id} failed: {e} retrying... task retries: {retries}")
            update_tasks_feild(task_id,status="retrying",retry_count=retries+1)
            raise self.retry(exc=e, countdown=2**retries)