import asyncio
from datetime import datetime, timedelta, timezone
from src.taskscheduling.services import update_tasks_feild
from ..config import config
from fastapi import FastAPI, HTTPException
from .tasks import execute_task
from Logger import logger

async def schedule_loop(delay, app: FastAPI):
    pool = app.state.pools[config.URI]
    logger.info("Scheduler loop started with delay: %s seconds", delay)
    while True:
        try:
            async with pool.connection() as connection:
                result = await connection.execute("""
                WITH selected AS (
                    SELECT task_id FROM tasks
                    WHERE status IN ('pending')
                    AND scheduled_time <= NOW()
                    ORDER BY
                        CASE priority
                            WHEN 'high'   THEN 1
                            WHEN 'medium' THEN 2
                            ELSE 3
                        END ASC,
                        created_at ASC
                    LIMIT 10
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE tasks
                SET status = 'queued'
                FROM selected
                WHERE tasks.task_id = selected.task_id
                RETURNING tasks.task_id, tasks.task_type
            """)

                rows =await result.fetchall()
            
        except Exception as e:
            logger.error(f"Error fetching tasks for scheduling: {e}")
            raise HTTPException(status_code=500, detail={"message": "Error fetching tasks for scheduling", "error": str(e)})
        for row in rows:
            task_type = row["task_type"]
            logger.info(f"Fetched tasks for scheduling task type: {task_type}.")
            execute_task.delay(str(row["task_id"])) # type: ignore
        await asyncio.sleep(delay)
    