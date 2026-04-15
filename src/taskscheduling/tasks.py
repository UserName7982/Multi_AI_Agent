from datetime import datetime, timedelta, timezone
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
        if data is not None and data["task_type"]=="email_fetch": # type: ignore
            update_tasks_feild(task_id,status="pending",completed_at=now,scheduled_time=now+timedelta(hours=4),next_run_time=now+timedelta(hours=4))
        else:
            update_tasks_feild(task_id,status="completed")
    except Exception as e:
        retries=self.request.retries
        if retries > 3:
            logger.error(f"Task with ID {task_id} failed after {retries} retries: {e}")
            update_tasks_feild(task_id,status="failed",completed_at=now)
        else:
            logger.error(f"Task with ID {task_id} failed: {e} retrying... task retries: {retries}")
            update_tasks_feild(task_id,status="retrying",retry_count=retries+1,completed_at=now)
            raise self.retry(exc=e, countdown=2**retries)