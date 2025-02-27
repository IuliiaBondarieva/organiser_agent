from typing import Dict, Any, List, Callable, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
from services.analytics_service import AnalyticsService
from services.prediction_service import PredictionService
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """State for the agent graph"""
    question: str
    context: Dict[str, Any]
    answer: str

class AgentService:
    def __init__(self, analytics_service: AnalyticsService, prediction_service: PredictionService):
        self.analytics_service = analytics_service
        self.prediction_service = prediction_service
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent graph"""
        # Define the tools
        tools = {
            "analyze_tasks": ToolNode(self.analytics_service.analyze_tasks),
            "analyze_habits": ToolNode(self.analytics_service.analyze_habits),
            "predict_task": self._predict_task_tool,
            "predict_habit": self._predict_habit_tool,
            "generate_insights": self._generate_insights_tool
        }
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_tasks", tools["analyze_tasks"])
        workflow.add_node("analyze_habits", tools["analyze_habits"])
        workflow.add_node("predict_task", tools["predict_task"])
        workflow.add_node("predict_habit", tools["predict_habit"])
        workflow.add_node("generate_insights", tools["generate_insights"])
        
        # Define edges
        workflow.add_edge("analyze_tasks", "analyze_habits")
        workflow.add_edge("analyze_habits", "generate_insights")
        workflow.add_edge("generate_insights", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_tasks")
        
        # Compile the graph
        return workflow.compile()
    
    def _predict_task_tool(self, state: AgentState) -> AgentState:
        """Tool for predicting task completion"""
        # Get the first task ID for demonstration
        tasks = self.analytics_service.supabase_service.get_tasks()
        if tasks:
            task_id = tasks[0].id
            prediction = self.prediction_service.predict_task_completion(task_id)
            state["context"]["task_prediction"] = prediction
        return state
    
    def _predict_habit_tool(self, state: AgentState) -> AgentState:
        """Tool for predicting habit completion"""
        # Get the first habit ID for demonstration
        habits = self.analytics_service.supabase_service.get_habits()
        if habits:
            habit_id = habits[0].id
            prediction = self.prediction_service.predict_habit_completion(habit_id)
            state["context"]["habit_prediction"] = prediction
        return state
    
    def _generate_insights_tool(self, state: AgentState) -> AgentState:
        """Tool for generating insights from analytics data"""
        task_analytics = state["context"].get("task_analytics", {})
        habit_analytics = state["context"].get("habit_analytics", {})
        
        insights = []
        
        # Task insights
        if task_analytics:
            completion_rate = task_analytics.get("completion_rate", 0)
            insights.append(f"Task completion rate: {completion_rate:.1f}%")
            
            avg_completion_time = task_analytics.get("avg_completion_time_hours", 0)
            insights.append(f"Average task completion time: {avg_completion_time:.1f} hours")
            
            tasks_by_priority = task_analytics.get("tasks_by_priority", {})
            if tasks_by_priority:
                high_priority = tasks_by_priority.get(5, 0) + tasks_by_priority.get(4, 0)
                insights.append(f"High priority tasks: {high_priority}")
        
        # Habit insights
        if habit_analytics:
            habit_completion_rate = habit_analytics.get("habit_completion_rate", 0)
            insights.append(f"Habit completion rate: {habit_completion_rate:.1f}%")
            
            avg_streak = habit_analytics.get("avg_streak", 0)
            insights.append(f"Average habit streak: {avg_streak:.1f} days")
            
            habit_consistency = habit_analytics.get("habit_consistency", {})
            if habit_consistency:
                most_consistent = next(iter(habit_consistency.items()), None)
                if most_consistent:
                    habit_name, consistency = most_consistent
                    insights.append(f"Most consistent habit: {habit_name} ({consistency*100:.1f}%)")
        
        state["answer"] = "\n".join(insights)
        return state
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate insights using the LangGraph agent"""
        # Initialize state
        initial_state = {
            "question": "Generate insights from task and habit data",
            "context": {},
            "answer": ""
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Get task and habit analytics
        task_analytics = self.analytics_service.analyze_tasks()
        habit_analytics = self.analytics_service.analyze_habits()
        
        # Get predictions for a sample task and habit
        tasks = self.analytics_service.supabase_service.get_tasks()
        habits = self.analytics_service.supabase_service.get_habits()
        
        task_prediction = None
        if tasks:
            task_prediction = self.prediction_service.predict_task_completion(tasks[0].id)
        
        habit_prediction = None
        if habits:
            habit_prediction = self.prediction_service.predict_habit_completion(habits[0].id)
        
        return {
            "insights": result["answer"],
            "task_analytics": task_analytics,
            "habit_analytics": habit_analytics,
            "sample_task_prediction": task_prediction,
            "sample_habit_prediction": habit_prediction
        }