import asyncio
from ..config import config
from fastapi import FastAPI
from .tasks import execute_task
from Logger import logger

async def schedule_loop(delay, app: FastAPI):
    pool = app.state.pools[config.URI]
    logger.info("Scheduler loop started with delay: %s seconds", delay)
    while True:
        try:
            async with pool.connection() as connection:
                result = await connection.execute("""
                    UPDATE tasks
                    SET status = 'queued'
                    WHERE task_id IN (
                        SELECT task_id FROM tasks
                        WHERE status IN ('pending', 'queued')
                        AND scheduled_time <= NOW()
                        ORDER BY 
                            CASE priority 
                                WHEN 'high'   THEN 1 
                                WHEN 'medium' THEN 2 
                                ELSE 3 
                            END ASC,
                            created_at ASC
                        LIMIT 50
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING task_id;
                """)

                rows =await result.fetchall()
            
        except Exception as e:
            logger.error(f"Error fetching tasks for scheduling: {e}")
            continue
        for row in rows:
            logger.info(f"Fetched tasks for scheduling.")
            execute_task.delay(str(row["task_id"])) # type: ignore
        await asyncio.sleep(delay)
    