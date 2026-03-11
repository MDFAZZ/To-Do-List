# To-Do List Application

This is a simple task management web application built using Django.
It allows users to create, view, update, and delete tasks through both a web interface and REST API.

The main goal of this project was to build a clean backend structure, use raw SQL instead of Django ORM, and include proper logging, testing, and documentation.

---

## Features

* Create, read, update, and delete tasks
* Each task contains:

  * title
  * description
  * due date
  * status (pending / completed)
* REST API endpoints for task management
* Simple web interface to manage tasks
* Raw SQL queries used for database operations
* Logging and exception handling
* Unit and API testing using pytest
* API documentation using Swagger
* Docker support

---

## Tech Stack

* Python 3.12
* Django 4.2
* SQLite
* pytest / pytest-django
* Swagger (drf-yasg)
* HTML / CSS / JavaScript
* Docker & Docker Compose

---

## Project Setup

### 1. Clone the Repository

Note URL: https://github.com/MDFAZZ/To-Do-List.git
```bash
git clone <repository-url>
cd pelocal
```

---

### 2. Create a Virtual Environment

**Prerequisites:** Python 3.12 must be installed on your system.

Linux / Mac:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python3.12 -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Initialize the Database

Run the Django shell:

```bash
python manage.py shell
```

Then run:

```python
from tasks.database import initialize_database
initialize_database()
exit()
```

---

### 5. Create Logs Directory

```bash
mkdir logs
```

---

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will run at:

```
http://localhost:8000
```

---

## Running with Docker

If Docker is installed, the project can also be run using Docker Compose.

Start the application:

```bash
docker-compose up --build
```

Access the application:

* Web App → http://localhost:8000
* Swagger UI → http://localhost:8000/swagger/

Stop containers:

```bash
docker-compose down
```

View logs:

```bash
docker-compose logs -f web
```

## Using the Application

### Web Interface

Main page:

```
http://localhost:8000
```

From the web interface you can:

* View all tasks
* Add new tasks
* Mark tasks as completed
* Delete tasks

---

## API Documentation

Swagger UI:

```
http://localhost:8000/swagger/
```

## API Endpoints

Base endpoint:

```
/api/tasks/
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
-H "Content-Type: application/json" \
-d '{"title":"Task 1","description":"Example task","status":"pending"}'
```

### Get All Tasks

```bash
curl http://localhost:8000/api/tasks
```

### Get Task by ID

```bash
curl http://localhost:8000/api/tasks/1/
```

### Update Task

```bash
curl -X PUT http://localhost:8000/api/tasks/1/update/ \
-H "Content-Type: application/json" \
-d '{"status":"completed"}'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1/delete/
```

---

## Running Tests

Run all tests:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=tasks --cov-report=html
```

Run specific test file:

```bash
pytest tasks/tests.py
```

The test suite includes:

* Service layer tests
* API endpoint tests
* Database operation tests
* Error handling tests

---

## Project Structure

```
To-Do-List/
│
│
├── todolist_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── tasks/
│   ├── database.py
│   ├── task_service.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── templates/
│   └── tasks/
│
├── static/
│   ├── css/
│   └── js/
│
├── logs/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── pytest.ini
├── README.md
```

---

## Notes

* Django ORM is not used in this project.
  All database operations are implemented using raw SQL queries.

* Business logic is separated into a service layer (`task_service.py`).

* Logging is enabled for easier debugging and monitoring.

---

### Database Issues

Delete the SQLite database and recreate it:

```bash
rm db.sqlite3
```

Then initialize the database again.

---

### Port Already in Use

Run the server on another port:

```bash
python manage.py runserver 8001
```

---

