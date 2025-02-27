import os
from supabase import create_client, Client
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.task import Task
from models.habit import Habit, HabitLog

class SupabaseService:
    def __init__(self):
        # Get Supabase credentials from environment variables
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def get_tasks(self) -> List[Task]:
        """Retrieve all tasks from Supabase"""
        response = self.supabase.table("tasks").select("*").execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching tasks: {response.error}")
        
        return [Task(**task) for task in response.data]
    
    def get_task(self, task_id: int) -> Task:
        """Retrieve a specific task by ID"""
        response = self.supabase.table("tasks").select("*").eq("id", task_id).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching task: {response.error}")
        
        if not response.data:
            raise Exception(f"Task with ID {task_id} not found")
        
        return Task(**response.data[0])
    
    def get_habits(self) -> List[Habit]:
        """Retrieve all habits from Supabase"""
        response = self.supabase.table("habits").select("*").execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching habits: {response.error}")
        
        habits = []
        for habit_data in response.data:
            # Get habit logs
            logs_response = self.supabase.table("habit_logs").select("*").eq("habit_id", habit_data["id"]).execute()
            
            if hasattr(logs_response, 'error') and logs_response.error:
                raise Exception(f"Error fetching habit logs: {logs_response.error}")
            
            habit_data["logs"] = [HabitLog(**log) for log in logs_response.data]
            habits.append(Habit(**habit_data))
        
        return habits
    
    def get_habit(self, habit_id: int) -> Habit:
        """Retrieve a specific habit by ID"""
        response = self.supabase.table("habits").select("*").eq("id", habit_id).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching habit: {response.error}")
        
        if not response.data:
            raise Exception(f"Habit with ID {habit_id} not found")
        
        habit_data = response.data[0]
        
        # Get habit logs
        logs_response = self.supabase.table("habit_logs").select("*").eq("habit_id", habit_id).execute()
        
        if hasattr(logs_response, 'error') and logs_response.error:
            raise Exception(f"Error fetching habit logs: {logs_response.error}")
        
        habit_data["logs"] = [HabitLog(**log) for log in logs_response.data]
        
        return Habit(**habit_data)
    
    def get_user_tasks(self, user_id: str) -> List[Task]:
        """Retrieve all tasks for a specific user"""
        response = self.supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching user tasks: {response.error}")
        
        return [Task(**task) for task in response.data]
    
    def get_user_habits(self, user_id: str) -> List[Habit]:
        """Retrieve all habits for a specific user"""
        response = self.supabase.table("habits").select("*").eq("user_id", user_id).execute()
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Error fetching user habits: {response.error}")
        
        habits = []
        for habit_data in response.data:
            # Get habit logs
            logs_response = self.supabase.table("habit_logs").select("*").eq("habit_id", habit_data["id"]).execute()
            
            if hasattr(logs_response, 'error') and logs_response.error:
                raise Exception(f"Error fetching habit logs: {logs_response.error}")
            
            habit_data["logs"] = [HabitLog(**log) for log in logs_response.data]
            habits.append(Habit(**habit_data))
        
        return habits