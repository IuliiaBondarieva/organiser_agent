from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class HabitLog(BaseModel):
    date: datetime
    completed: bool

class Habit(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    frequency: str  # daily, weekly, monthly
    target_days: List[int] = []  # e.g., [0, 2, 4] for Mon, Wed, Fri
    streak: int = 0
    logs: List[HabitLog] = []
    user_id: str
    created_at: datetime
    updated_at: datetime