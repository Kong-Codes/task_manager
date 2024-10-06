import psycopg2
import logging
import os
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from .exceptions import ConnectToDatabaseError, CreateTableError, ValidationError
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    """
    This function creates a connection to the database
    """
    try:
        connection = psycopg2.connect(DATABASE_URL)
        return connection
    except Exception as e:
        raise ConnectToDatabaseError("cannot connect to postgres database") from e


def create_table(connection):
    query1 = """
    CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
     username VARCHAR(100) UNIQUE,
      password VARCHAR(100),
       email VARCHAR(100) UNIQUE,
        full_name VARCHAR(100),
        is_active BOOLEAN DEFAULT True,
        PRIMARY KEY(user_id)); 
    """
    query2 = """
    CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER,
    user_id INTEGER,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    deadline DATE,
    importance INTEGER DEFAULT 1,
    is_completed BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(task_id), 
    CONSTRAINT fk_users
        FOREIGN KEY(user_id) 
        REFERENCES users(user_id));
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query1)
        cursor.execute(query2)
        connection.commit()
        cursor.close()
        logging.info("table created successfully")
    except Exception as e:
        raise CreateTableError("cannot create table") from e


def insert_user_details(connection, user, hashed_password):
    insert_script = ("INSERT INTO users (user_id, username, password, email, full_name) "
                     "VALUES (%s, %s, %s, %s, %s) RETURNING *;")
    insert_values = (f"{user.id}", f"{user.username}", f"{hashed_password}", f"{user.email}", f"{user.full_name}")
    cur = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(insert_script, insert_values)
        connection.commit()
        return cur.fetchone()
    except psycopg2.Error as e:
        connection.rollback()
        raise e
    finally:
        cur.close()


def task_data(connection, task, user_id):
    insert_script = ("INSERT INTO tasks (task_id, title, description, deadline, importance, user_id) "
                     "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;")
    insert_values = (f"{task.task_id}", f"{task.title}", f"{task.description}", f"{task.deadline}", f"{task.importance}",
                     f"{user_id}")
    cur = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(insert_script, insert_values)
        connection.commit()
        return cur.fetchone()
    except psycopg2.Error as e:
        connection.rollback()
        raise e
    finally:
        cur.close()


def validate_user_data(connection, username, password):
    query = ("SELECT username, password FROM users"
             f"WHERE username='{username} AND password='{password}';")
    try:
        cur = connection.cursor(cursor_factory=RealDictCursor)
        cur.excute(query)
        connection.commit()
        return cur.fetchone()
    except Exception as e:
        raise ValidationError("Invalid user") from e


def validate_username(connection, user):
    query = f"SELECT username FROM users WHERE username = '{user.username}';"
    try:
        cur = connection.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        username = cur.fetchone()
        cur.close()
        return username
    except Exception as e:
        raise ValidationError("Invalid user") from e


def get_user(connection, name):
    query = f"SELECT user_id, username, password FROM users WHERE username = '{name}';"
    cur = connection.cursor(cursor_factory=RealDictCursor)
    cur.execute(query)
    username = cur.fetchone()
    cur.close()
    return username


def get_task(connection, user):
    query = f"SELECT * FROM tasks WHERE user_id = '{user}';"
    try:
        cur = connection.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        tasks = cur.fetchall()
        cur.close()
        return tasks
    except Exception as e:
        raise ValidationError("Invalid user") from e


def update_task(connection, update_tasks, task_id):
    query = (f"UPDATE tasks SET title = '{update_tasks.title}', description = '{update_tasks.description}',"
             f" deadline = '{update_tasks.deadline}',importance = '{update_tasks.importance}',"
             f" is_completed = '{update_tasks.completed}' "
             f"WHERE task_id = '{task_id}' RETURNING *;")
    cur = connection.cursor(cursor_factory=RealDictCursor)
    cur.execute(query)
    connection.commit()
    updated_task = cur.fetchone()
    cur.close()
    return updated_task


def delete_task(connection, task_id):
    query = f"DELETE FROM tasks WHERE task_id = '{task_id}' RETURNING user_id;"
    cur = connection.cursor()
    cur.execute(query)
    connection.commit()
    deleted_task_id = cur.fetchone()
    cur.close()
    return deleted_task_id
