from celery import Celery

app = Celery("tasks",broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True
)