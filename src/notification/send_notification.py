from ..notification.server import servers
from Logger import logger
import redis.asyncio as redis

async def send_notifications():
    logger.info("Started notification Service...")
    try:
        r=redis.Redis(host='localhost', port=6379, db=0)
        pubsub=r.pubsub()
        await pubsub.subscribe("notification")
        async for msg in pubsub.listen():
            if msg["type"] == "message":
                await servers.broadcast(msg["data"].decode("utf-8"))
                print(f"Sent notification: {msg['data'].decode('utf-8')}")
    except Exception as e:
        logger.error(f"Error in sending notification: {e}")
    
