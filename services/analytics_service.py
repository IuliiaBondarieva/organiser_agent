import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from services.supabase_service import SupabaseService

class AnalyticsService:
    def __init__(self, supabase_service: SupabaseService):
        self.supabase_service = supabase_service
    
    def analyze_tasks(self) -> Dict[str, Any]:
        """Analyze task data to extract insights"""
        tasks = self.supabase_service.get_tasks()
        
        if not tasks:
            return {"message": "No tasks found for analysis"}
        
        # Convert to DataFrame for easier analysis
        task_df = pd.DataFrame([task.dict() for task in tasks])
        
        # Calculate completion rate
        completion_rate = task_df["completed"].mean() * 100
        
        # Calculate average time to complete tasks
        completed_tasks = task_df[task_df["completed"] == True]
        if not completed_tasks.empty:
            completed_tasks["completion_time"] = (
                completed_tasks["completed_at"] - completed_tasks["created_at"]
            ).dt.total_seconds() / 3600  # in hours
            avg_completion_time = completed_tasks["completion_time"].mean()
        else:
            avg_completion_time = 0
        
        # Tasks by priority
        tasks_by_priority = task_df.groupby("priority").size().to_dict()
        
        # Tasks by tag
        all_tags = []
        for tags in task_df["tags"]:
            all_tags.extend(tags)
        
        tags_count = {}
        for tag in all_tags:
            if tag in tags_count:
                tags_count[tag] += 1
            else:
                tags_count[tag] = 1
        
        # Tasks completed over time (last 30 days)
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        task_df["date"] = task_df["completed_at"].dt.date
        tasks_over_time = (
            task_df[
                (task_df["completed"] == True) & 
                (task_df["completed_at"] >= thirty_days_ago)
            ]
            .groupby("date")
            .size()
            .reset_index()
            .rename(columns={0: "count"})
        )
        
        tasks_over_time_dict = {
            str(row["date"]): row["count"] for _, row in tasks_over_time.iterrows()
        }
        
        return {
            "completion_rate": completion_rate,
            "avg_completion_time_hours": avg_completion_time,
            "tasks_by_priority": tasks_by_priority,
            "tasks_by_tag": tags_count,
            "tasks_over_time": tasks_over_time_dict,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(tasks) - len(completed_tasks)
        }
    
    def analyze_habits(self) -> Dict[str, Any]:
        """Analyze habit data to extract insights"""
        habits = self.supabase_service.get_habits()
        
        if not habits:
            return {"message": "No habits found for analysis"}
        
        # Convert to DataFrame for easier analysis
        habit_df = pd.DataFrame([habit.dict() for habit in habits])
        
        # Explode logs to analyze completion
        logs_data = []
        for habit in habits:
            for log in habit.logs:
                logs_data.append({
                    "habit_id": habit.id,
                    "habit_title": habit.title,
                    "date": log.date,
                    "completed": log.completed
                })
        
        logs_df = pd.DataFrame(logs_data)
        
        # Calculate overall habit completion rate
        if not logs_df.empty:
            habit_completion_rate = logs_df["completed"].mean() * 100
        else:
            habit_completion_rate = 0
        
        # Habits by frequency
        habits_by_frequency = habit_df.groupby("frequency").size().to_dict()
        
        # Average streak
        avg_streak = habit_df["streak"].mean()
        
        # Habit completion over time (last 30 days)
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        if not logs_df.empty:
            logs_df["date_only"] = logs_df["date"].dt.date
            habits_over_time = (
                logs_df[logs_df["date"] >= thirty_days_ago]
                .groupby(["date_only", "completed"])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            
            if True in habits_over_time.columns:
                habits_over_time["completion_rate"] = (
                    habits_over_time[True] / (habits_over_time[True] + habits_over_time[False]) * 100
                )
            else:
                habits_over_time["completion_rate"] = 0
            
            habits_over_time_dict = {
                str(row["date_only"]): row["completion_rate"] 
                for _, row in habits_over_time.iterrows()
            }
        else:
            habits_over_time_dict = {}
        
        # Most consistent habits (highest completion rate)
        if not logs_df.empty:
            habit_consistency = (
                logs_df.groupby("habit_title")["completed"]
                .mean()
                .sort_values(ascending=False)
                .to_dict()
            )
        else:
            habit_consistency = {}
        
        return {
            "habit_completion_rate": habit_completion_rate,
            "habits_by_frequency": habits_by_frequency,
            "avg_streak": avg_streak,
            "habits_over_time": habits_over_time_dict,
            "habit_consistency": habit_consistency,
            "total_habits": len(habits)
        }