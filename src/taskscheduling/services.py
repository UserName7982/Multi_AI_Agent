import json
from fastapi import FastAPI
from src.config import config
from Logger import logger
from ..taskscheduling.schema import Response
from ..DB.postgres import PoolManager
def get_task(task_id):
    logger.info(f"Fetching task with ID: {task_id}")
    conn=PoolManager.get_sync_pool(config.URI)
    try:
        with conn.connection() as connection:
            dict_row=connection.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        result=dict_row.fetchall()
        if not result:
            logger.error(f"Task with ID {task_id} not found.")
            return None
        return result
    except Exception as e: 
        logger.error(f"Error fetching task with ID {task_id}: {e}")
        return None

def update_task_status(task_id, status):
    conn= PoolManager.get_sync_pool(config.URI)
    try:
        with conn.connection() as connection:
            connection.execute("UPDATE tasks SET status = %s WHERE task_id = %s", (status, task_id))
        logger.info(f"Task with ID {task_id} updated to status: {status}")
    except Exception as e: 
        logger.error(f"Error updating task with ID {task_id} to status {status}: {e}")

def putting_task(response: Response):
    logger.info(f"Inserting task with ID: {response.task_id}")
    conn=PoolManager.get_sync_pool(config.URI)
    try:
        with conn.connection() as connection:
            connection.execute("""
                INSERT INTO tasks (task_id, task_type, status, priority, payload, result, schedule_type, scheduled_time, interval_seconds, next_run_time, started_at, completed_at, retry_count)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
            """, (
                response.task_id,
                response.task_type,
                response.status,
                response.priority,
                json.dumps(response.payload),
                json.dumps(response.result),
                response.schedule_type,
                response.scheduled_time,
                response.interval_seconds,
                response.next_run_time,
                response.started_at,
                response.completed_at,
                response.retry_count
            ))
        logger.info(f"Task with ID {response.task_id} inserted successfully.")
    except Exception as e: 
        logger.error(f"Error inserting task with ID {response.task_id}: {e}")
