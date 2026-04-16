from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel


class Response(BaseModel):
    task_id:uuid.UUID
    task_type :str          
    status: str           
    priority: str         
    payload :dict                    
    result: dict                    
    schedule_type :str              
    scheduled_time: datetime         
    interval_seconds : int          
    next_run_time : datetime                  
    started_at :datetime 
    completed_at :datetime 
    retry_count :Optional[int]=0