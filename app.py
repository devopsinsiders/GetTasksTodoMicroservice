import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os

# Fetch the connection string from the environment variable
connection_string = os.environ.get('CONNECTION_STRING')

# Check if the connection string is available
if connection_string:
    print(f"Connection String: {connection_string}")
else:
    print("Connection string not found in environment variables.")
    
app = FastAPI()

# Configure CORSMiddleware to allow all origins (disable CORS for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins (use '*' for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the Task model
class Task(BaseModel):
    title: str
    description: str

# Create a table for tasks (You can run this once outside of the app)
@app.get("/")
def create_tasks_table():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE Tasks (
                ID int NOT NULL PRIMARY KEY IDENTITY,
                Title varchar(255),
                Description text
            );
        """)
        conn.commit() 
        return "Get Tasks API Ready."       
    except Exception as e:
        print(e)
        if "There is already an object named 'Tasks' in the database." in str(e):
            return "Get Tasks API Ready."
        else:
            return "Error. Please check Logs."

# List all tasks
@app.get("/tasks")
def get_tasks():
    tasks = []
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks")
        for row in cursor.fetchall():
            task = {
                "ID": row.ID,
                "Title": row.Title,
                "Description": row.Description
            }
            tasks.append(task)
    return tasks

# Retrieve a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks WHERE ID = ?", task_id)
        row = cursor.fetchone()
        if row:
            task = {
                "ID": row.ID,
                "Title": row.Title,
                "Description": row.Description
            }
            return task
        return {"message": "Task not found"}

if __name__ == "__main__":
    create_tasks_table()
