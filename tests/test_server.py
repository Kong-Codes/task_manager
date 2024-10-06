import pytest
from fastapi.testclient import TestClient
from ..src.server import app  # Import the FastAPI app
from ..database_setup.database import get_db
from psycopg2 import connect
from psycopg2.extras import RealDictCursor

# Create a TestClient for FastAPI
client = TestClient(app)


def override_get_db():
    conn = connect(
        host="localhost",
        database="Data-Epic",
        user="mac",
        password="timmy1202",
        port="5432",
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()


app.dependency_overrides[get_db] = override_get_db


# Example Test User Data


@pytest.fixture(scope="module")
def setup_db():
    """
    Setup the test database and tables.
    Run this fixture once before all tests in the module.
    """
    conn = connect(
        host="localhost",
        database="Data-Epic",
        user="mac",
        port="5432",
        password="timmy1202"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
     username VARCHAR(100) UNIQUE,
      password VARCHAR(100),
       email VARCHAR(100) UNIQUE,
        full_name VARCHAR(100),
        is_active BOOLEAN DEFAULT True,
        PRIMARY KEY(user_id));
    """)
    cursor.execute("""
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
        REFERENCES users(user_id))
    """)
    conn.commit()
    cursor.close()
    conn.close()

    yield

    # Cleanup after tests
    conn = connect(
        host="localhost",
        database="Data-Epic",
        user="mac",
        port="5432",
        password="timmy1202"
    )
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tasks;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.mark.usefixtures("setup_db")
def test_register_user():
    # Simulate a new user registration
    test_user = {
        "id": 1231,
        "username": "kong",
        "password": "timileyin",
        "email": "sadiquetimileyin@gmail.com",
        "is_active": True,
        "full_name": "sadique timileyin"
    }
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    # assert response.json() == {"msg": "User registered successfully"}  # Expected response


def test_login_for_access_token():
    # Simulate login and token retrieval
    login_data = {
        "username": "kong",
        "password": "timileyin"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_create_task():
    login_data = {
        "username": "kong",
        "password": "timileyin"
    }
    login_response = client.post("/token", data=login_data)
    access_token = login_response.json()["access_token"]

    task_data = {
        "task_id": 22,
        "title": "test data",
        "description": "testing task creation",
        "deadline": "2024-10-04T08:35:00.351Z",
        "importance": 1,
    }

    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "test data"


def test_get_tasks():
    # Simulate getting user tasks
    login_data = {
        "username": "kong",
        "password": "timileyin"
    }
    login_response = client.post("/token", data=login_data)
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_task():
    # Simulate updating a task
    login_data = {
        "username": "kong",
        "password": "timileyin"
    }
    login_response = client.post("/token", data=login_data)
    access_token = login_response.json()["access_token"]

    task_data = {
        "title": "Updated Task",
        "description": "testing task creation",
        "deadline": "2024-10-04T08:35:00.351Z",
        "completed": True
    }

    task_id = 22
    response = client.put(
        f"/tasks/{task_id}",
        json=task_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"


def test_delete_task():
    login_data = {
        "username": "kong",
        "password": "timileyin"
    }
    login_response = client.post("/token", data=login_data)
    access_token = login_response.json()["access_token"]

    task_id = 22
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

