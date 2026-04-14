from datetime import datetime, timezone
from ..taskscheduling.handle_task import handle_task
from ..taskscheduling.services import update_tasks_feild
from celery import shared_task
from Logger import logger
from ..taskscheduling.services import get_task
@shared_task(max_retries=3,name="task.execute_task",bind=True)
def execute_task(self,task_id):
    update_tasks_feild(task_id,status="running")
    data=get_task(task_id)
    now=datetime.now(timezone.utc)
    try:
        handle_task(task_id)
        logger.info(f"FULL DATA: {data}")
        logger.info(f"TASK TYPE RAW: {data.get('task_type')}")
        logger.info(f"TASK TYPE NORMALIZED: {str(data.get('task_type')).strip().lower()}")
        if data is not None and data["task_type"]=="email_fetch":

            update_tasks_feild(task_id,status="pending",completed_at=now)
        else:
            update_tasks_feild(task_id,status="completed",completed_at=now)
    except Exception as e:
        retries=self.request.retries
        if retries > 3:
            logger.error(f"Task with ID {task_id} failed after {retries} retries: {e}")
            update_tasks_feild(task_id,status="failed",completed_at=now)
        else:
            logger.error(f"Task with ID {task_id} failed: {e} retrying... task retries: {retries}")
            update_tasks_feild(task_id,status="retrying",retry_count=retries+1,completed_at=now)
            raise self.retry(exc=e, countdown=2**retries)