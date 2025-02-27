import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from services.supabase_service import SupabaseService

class PredictionService:
    def __init__(self, supabase_service: SupabaseService):
        self.supabase_service = supabase_service
        self.task_model = None
        self.habit_model = None
        self.task_encoder = None
        self.habit_encoder = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize and train prediction models"""
        # Train task completion prediction model
        tasks = self.supabase_service.get_tasks()
        if tasks:
            task_df = pd.DataFrame([task.dict() for task in tasks])
            
            # Feature engineering for tasks
            task_df["day_of_week"] = task_df["due_date"].dt.dayofweek
            task_df["month"] = task_df["due_date"].dt.month
            task_df["days_to_complete"] = (task_df["due_date"] - task_df["created_at"]).dt.days
            
            # One-hot encode categorical features
            categorical_features = ["priority"]
            if categorical_features:
                self.task_encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
                encoded_features = self.task_encoder.fit_transform(task_df[categorical_features])
                
                # Create feature names
                feature_names = self.task_encoder.get_feature_names_out(categorical_features)
                
                # Create DataFrame with encoded features
                encoded_df = pd.DataFrame(encoded_features, columns=feature_names)
                
                # Concatenate with original DataFrame
                task_df = pd.concat([task_df.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
            
            # Select features and target
            X = task_df[["day_of_week", "month", "days_to_complete"] + list(feature_names)]
            y = task_df["completed"]
            
            # Train model
            self.task_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.task_model.fit(X, y)
        
        # Train habit completion prediction model
        habits = self.supabase_service.get_habits()
        if habits:
            # Extract habit logs
            logs_data = []
            for habit in habits:
                for log in habit.logs:
                    logs_data.append({
                        "habit_id": habit.id,
                        "habit_title": habit.title,
                        "frequency": habit.frequency,
                        "date": log.date,
                        "completed": log.completed,
                        "streak": habit.streak
                    })
            
            if logs_data:
                logs_df = pd.DataFrame(logs_data)
                
                # Feature engineering for habits
                logs_df["day_of_week"] = logs_df["date"].dt.dayofweek
                logs_df["month"] = logs_df["date"].dt.month
                logs_df["day_of_month"] = logs_df["date"].dt.day
                
                # One-hot encode categorical features
                categorical_features = ["frequency"]
                if categorical_features:
                    self.habit_encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
                    encoded_features = self.habit_encoder.fit_transform(logs_df[categorical_features])
                    
                    # Create feature names
                    feature_names = self.habit_encoder.get_feature_names_out(categorical_features)
                    
                    # Create DataFrame with encoded features
                    encoded_df = pd.DataFrame(encoded_features, columns=feature_names)
                    
                    # Concatenate with original DataFrame
                    logs_df = pd.concat([logs_df.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
                
                # Select features and target
                X = logs_df[["day_of_week", "month", "day_of_month", "streak"] + list(feature_names)]
                y = logs_df["completed"]
                
                # Train model
                self.habit_model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.habit_model.fit(X, y)
    
    def predict_task_completion(self, task_id: int) -> Dict[str, Any]:
        """Predict the likelihood of completing a specific task"""
        if not self.task_model:
            return {"message": "Prediction model not trained yet", "probability": 0.5}
        
        try:
            task = self.supabase_service.get_task(task_id)
            
            # Feature engineering
            features = {
                "day_of_week": task.due_date.weekday(),
                "month": task.due_date.month,
                "days_to_complete": (task.due_date - task.created_at).days
            }
            
            # One-hot encode categorical features
            if self.task_encoder:
                categorical_features = {"priority": task.priority}
                encoded_features = self.task_encoder.transform(pd.DataFrame([categorical_features]))
                
                # Get feature names
                feature_names = self.task_encoder.get_feature_names_out(["priority"])
                
                # Add encoded features to features dictionary
                for i, name in enumerate(feature_names):
                    features[name] = encoded_features[0, i]
            
            # Convert features to DataFrame
            X = pd.DataFrame([features])
            
            # Predict probability
            probability = self.task_model.predict_proba(X)[0, 1]
            
            # Get feature importances
            feature_importances = dict(zip(X.columns, self.task_model.feature_importances_))
            
            return {
                "task_id": task_id,
                "task_title": task.title,
                "completion_probability": float(probability),
                "likely_to_complete": probability > 0.5,
                "feature_importances": feature_importances
            }
        
        except Exception as e:
            return {"message": f"Error predicting task completion: {str(e)}", "probability": 0.5}
    
    def predict_habit_completion(self, habit_id: int) -> Dict[str, Any]:
        """Predict the likelihood of completing a specific habit"""
        if not self.habit_model:
            return {"message": "Prediction model not trained yet", "probability": 0.5}
        
        try:
            habit = self.supabase_service.get_habit(habit_id)
            
            # Use today's date for prediction
            today = datetime.now()
            
            # Feature engineering
            features = {
                "day_of_week": today.weekday(),
                "month": today.month,
                "day_of_month": today.day,
                "streak": habit.streak
            }
            
            # One-hot encode categorical features
            if self.habit_encoder:
                categorical_features = {"frequency": habit.frequency}
                encoded_features = self.habit_encoder.transform(pd.DataFrame([categorical_features]))
                
                # Get feature names
                feature_names = self.habit_encoder.get_feature_names_out(["frequency"])
                
                # Add encoded features to features dictionary
                for i, name in enumerate(feature_names):
                    features[name] = encoded_features[0, i]
            
            # Convert features to DataFrame
            X = pd.DataFrame([features])
            
            # Predict probability
            probability = self.habit_model.predict_proba(X)[0, 1]
            
            # Get feature importances
            feature_importances = dict(zip(X.columns, self.habit_model.feature_importances_))
            
            return {
                "habit_id": habit_id,
                "habit_title": habit.title,
                "completion_probability": float(probability),
                "likely_to_complete": probability > 0.5,
                "feature_importances": feature_importances
            }
        
        except Exception as e:
            return {"message": f"Error predicting habit completion: {str(e)}", "probability": 0.5}