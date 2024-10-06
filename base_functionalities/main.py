import logging
from passlib.context import CryptContext
from ..src.model import CreateUser, UserInDB, TaskData, Task

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def password_hasher(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username):
    from ..database_setup.database import get_db, get_user
    util = get_db()
    db = get_user(util, username)
    if db is None:
        return None
    else:
        return db


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


# def save_user(user_in: UserInDB):
#     hashed_password = password_hasher(user_in.password)
#     user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
#     logging.info("User saved!")
#     return user_in_db
#
#
# def save_task(task: TaskData):
#     task_in_db = TaskData(**task.dict())
#     return task_in_db

