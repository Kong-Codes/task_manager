from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status
from ..database_setup.database import get_db
from ..base_functionalities.main import authenticate_user, password_hasher
from ..base_functionalities.home import create_user, create_task, get_tasks, update_task, delete_tasks
from ..base_functionalities.authentication import get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .model import CreateUser, Task, Token, TaskData, TaskUpdate

description = """
Task Manager API helps you do awesome stuff. 🚀

## Tasks

You can **get tasks**.

## Users

You will be able to:

* **Create users**
* **Create tasks**
* **Update tasks**
* **Delete tasks** 
"""

app = FastAPI(
    title="TaskManager",
    description=description,
    summary="Task creation simplified into a fast api system.",
    version="0.0.1",

)


@app.post("/register")
def register(user: CreateUser, conn=Depends(get_db)):
    try:
        hash_password = password_hasher(user.password)
        return create_user(conn, user, hash_password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User already exists")


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/tasks/", response_model=Task)
def create_new_task(task: TaskData, conn=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        task_data = create_task(conn, task, current_user["user_id"])
        task_data = dict(task_data)
        return Task(**task_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Task already exists")


@app.get("/tasks/", response_model=list[Task])
def get_user_tasks(conn=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return get_tasks(conn, current_user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail="No Task found") from e


@app.put("/tasks/{task_id}", response_model=Task)
def update_existing_task(task_id: int, task: Task, conn=Depends(get_db), current_user=Depends(get_current_user)):
    updated_task = update_task(conn, task, task_id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/tasks/{task_id}")
def delete_existing_task(task_id: int, conn=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return delete_tasks(conn, task_id)
    except Exception as e:
        raise HTTPException(status_code=404,
                            detail="Task Id does not exist") from e
