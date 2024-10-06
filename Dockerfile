FROM python:3.11

WORKDIR /task_manager_api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "dev", "src/server.py", "--host", "0.0.0.0", "--port", "8000"]