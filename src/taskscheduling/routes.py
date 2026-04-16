from fastapi import APIRouter

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])

@tasks_router.get("/health")
async def health_check():
    return {"status": "ok"}
@tasks_router.post("/notify/{task_id}/approve")
async def notifying_approve():
    pass

@tasks_router.post("/notify/{task_id}/reject")
async def notifying_reject():
    pass

@tasks_router.post("/notify/{task_id}/remake")
async def notifying_remake():
    pass

@tasks_router.post("/notify/{task_id}/completed")
async def notifying_completed():
    pass