from pydantic import BaseModel, EmailStr
from datetime import datetime


class CreateUser(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr
    is_active: bool
    full_name: str | None = None


class UserInDB(CreateUser):
    hashed_password: str


class TaskData(BaseModel):
    task_id: int
    title: str
    description: str
    deadline: datetime | None = None
    importance: int = 1


class TaskUpdate(BaseModel):
    title: str
    description: str
    deadline: datetime
    completed: bool


class Task(TaskData):
    completed: bool = False
    user_id: int | None = None


class User(UserInDB):
    active: bool
    task: list[Task] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
