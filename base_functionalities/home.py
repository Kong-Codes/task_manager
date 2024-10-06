from ..database_setup.database import (insert_user_details, validate_username,
                       task_data, get_task, update_task, delete_task)


# Create User
def create_user(conn, user, hashed_password):
    return insert_user_details(conn, user, hashed_password)


# Get User by Username
def get_user_by_username(conn, user):
    return validate_username(conn, user)


# Create Task
def create_task(conn, task, user_id):
    return task_data(conn, task, user_id)


# Get Tasks for User
def get_tasks(conn, user):
    return get_task(conn, user)


# Update Task
def update_tasks(conn, task):
    return update_task(conn, task)


# Delete Task
def delete_tasks(conn, task_id):
    return delete_task(conn, task_id)
