import traceback
from ..notification.server import servers
from fastapi import Request,WebSocket,APIRouter,WebSocketDisconnect
from Logger import logger


notify_router=APIRouter(prefix="/notification",tags=["Notification"])

@notify_router.get("/health")
async def health_check(request: Request):
    return {"status": "ok"}

@notify_router.websocket("/ws")
async def web_socket_endpoint(websocket: WebSocket):
    await servers.connect(websocket=websocket)
    print("connected to web socket")
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received data
            print(f"Received data: {data}")
    except WebSocketDisconnect as e:
        await servers.disconnect(websocket=websocket)
        logger.error(f"Error in web_socket_endpoint:\n",extra={"error":traceback.format_exc()})
    except Exception as e:
        logger.error(f"Unexpected ERROR in web_socket_endpoint:\n",extra={"error":traceback.format_exc()})