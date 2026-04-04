import redis.asyncio as redis
from datetime import datetime
from ..api.schema import Message_Response

redis_client = redis.Redis(host='localhost', port=6379, db=0,decode_responses=True) # type: ignore

async def addmessage(thread_id,role,content,message_id):
    try:
        await redis_client.xadd(
     f"thread:{thread_id}",
    {   
        "thread_id": str(thread_id),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # current timestamp
        "message_id":str(message_id),
        "role": str(role),
        "content": content
    },
    maxlen=1000  # auto trim
  );
        await redis_client.expire(f"thread:{thread_id}", 60*60*24*7)  # expire after 7 days
    except Exception as e:
        print(e)

async def getmessages(thread_id):
    messages = await redis_client.xrange(f"thread:{thread_id}", min='-', max='+', count=1000)
    if not messages:
        return []
    result=[]
    for msg in messages:
        msg_data=msg[1]
        result.append(Message_Response(**{
            "thread_id": msg_data.get("thread_id"),
            "created_at": msg_data.get("created_at"),
            "message_id": (msg_data.get("message_id")),
            "role": msg_data.get("role"),
            "content": msg_data.get("content")
        }))
    return result


if __name__ == "__main__":
    import asyncio

    async def main():
        messages = await getmessages("b3739414-5f44-4617-a5cf-45485c023ccf")
        print(messages)

    asyncio.run(main())