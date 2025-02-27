# Organiser Backend

A Python service that uses LangGraph agent to pull data from Supabase database, perform data analysis, and make machine learning predictions for tasks and habits.

## Features

- Task and habit tracking
- Data analysis and visualization
- Machine learning predictions for task/habit completion likelihood
- LangGraph agent for orchestrating workflows
- RESTful API with FastAPI

## Installation

### Install backend dependencies

Make sure you have uv installed. If you don't, you can install it using pip:
```
pip install uv
```

```
uv pip install -r requirements.txt
```

### Run app

```
# Clone repository
git clone https://github.com/your-repo/organiser-backend.git
cd organiser-backend

# Run the server
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
export NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

uvicorn main:app --reload

uvicorn organiser_agent.main:app --host 0.0.0.0 --port 8000
```