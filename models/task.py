from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    priority: int = 1  # 1-5 scale
    tags: List[str] = []
    user_id: str
    created_at: datetime
    updated_at: datetime