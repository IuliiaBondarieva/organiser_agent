import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime, timedelta

from services.supabase_service import SupabaseService
from services.analytics_service import AnalyticsService
from services.prediction_service import PredictionService
from services.agent_service import AgentService
from models.task import Task
from models.habit import Habit
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Organiser API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
def get_supabase_service():
    return SupabaseService()

def get_analytics_service(supabase_service: SupabaseService = Depends(get_supabase_service)):
    return AnalyticsService(supabase_service)

def get_prediction_service(supabase_service: SupabaseService = Depends(get_supabase_service)):
    return PredictionService(supabase_service)

def get_agent_service(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    return AgentService(analytics_service, prediction_service)

@app.get("/")
def read_root():
    return {"message": "Welcome to Organiser API"}

@app.get("/tasks", response_model=List[Task])
def get_tasks(supabase_service: SupabaseService = Depends(get_supabase_service)):
    return supabase_service.get_tasks()

@app.get("/habits", response_model=List[Habit])
def get_habits(supabase_service: SupabaseService = Depends(get_supabase_service)):
    return supabase_service.get_habits()

@app.get("/analytics/tasks")
def get_task_analytics(analytics_service: AnalyticsService = Depends(get_analytics_service)):
    return analytics_service.analyze_tasks()

@app.get("/analytics/habits")
def get_habit_analytics(analytics_service: AnalyticsService = Depends(get_analytics_service)):
    return analytics_service.analyze_habits()

@app.get("/predictions/tasks/{task_id}")
def get_task_prediction(task_id: int, prediction_service: PredictionService = Depends(get_prediction_service)):
    return prediction_service.predict_task_completion(task_id)

@app.get("/predictions/habits/{habit_id}")
def get_habit_prediction(habit_id: int, prediction_service: PredictionService = Depends(get_prediction_service)):
    return prediction_service.predict_habit_completion(habit_id)

@app.get("/agent/insights")
def get_agent_insights(agent_service: AgentService = Depends(get_agent_service)):
    return agent_service.generate_insights()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)