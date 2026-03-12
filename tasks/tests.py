# Test suite for the todo app
# Using pytest and pytest-django for testing

import pytest
import json
from django.test import Client
from django.urls import reverse
from .database import initialize_database, get_db_connection
from .task_service import TaskService


@pytest.fixture(autouse=True)
def setup_database(db):
    # Clean up the database before and after each test
    # Makes sure tests don't interfere with each other
    from tasks.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
    
    initialize_database()
    yield
    # Cleanup after test runs
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()


@pytest.fixture
def client():
    # Django test client for making requests
    return Client()


class TestTaskService:
    # Tests for the service layer (business logic)
    
    def test_create_task_success(self):
        """Test successful task creation."""
        task = TaskService.create_task(
            title="Test Task",
            description="Test Description",
            due_date="2026-03-15",
            status="pending"
        )
        
        assert task is not None
        assert task['title'] == "Test Task"
        assert task['description'] == "Test Description"
        assert task['due_date'] == "2026-03-15"
        assert task['status'] == "pending"
        assert 'id' in task
        assert 'created_at' in task
        assert 'updated_at' in task
    
    def test_create_task_minimal(self):
        """Test task creation with only required fields."""
        task = TaskService.create_task(title="Minimal Task")
        
        assert task is not None
        assert task['title'] == "Minimal Task"
        assert task['description'] is None
        assert task['due_date'] is None
        assert task['status'] == "pending"
    
    def test_create_task_empty_title(self):
        """Test that creating a task with empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title is required"):
            TaskService.create_task(title="")
    
    def test_create_task_invalid_status(self):
        """Test that creating a task with invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Status must be"):
            TaskService.create_task(title="Test", status="invalid")
    
    def test_get_all_tasks_empty(self):
        """Test retrieving all tasks when database is empty."""
        tasks = TaskService.get_all_tasks()
        assert tasks == []
    
    def test_get_all_tasks_multiple(self):
        """Test retrieving multiple tasks."""
        TaskService.create_task(title="Task 1")
        TaskService.create_task(title="Task 2")
        TaskService.create_task(title="Task 3")
        
        tasks = TaskService.get_all_tasks()
        assert len(tasks) == 3
        assert all(task['title'] in ["Task 1", "Task 2", "Task 3"] for task in tasks)
    
    def test_get_task_by_id_success(self):
        """Test retrieving a task by ID."""
        created_task = TaskService.create_task(title="Find Me")
        task_id = created_task['id']
        
        retrieved_task = TaskService.get_task_by_id(task_id)
        assert retrieved_task is not None
        assert retrieved_task['id'] == task_id
        assert retrieved_task['title'] == "Find Me"
    
    def test_get_task_by_id_not_found(self):
        """Test retrieving a non-existent task."""
        task = TaskService.get_task_by_id(99999)
        assert task is None
    
    def test_update_task_success(self):
        """Test successful task update."""
        created_task = TaskService.create_task(title="Original Title")
        task_id = created_task['id']
        
        updated_task = TaskService.update_task(
            task_id=task_id,
            title="Updated Title",
            status="completed"
        )
        
        assert updated_task is not None
        assert updated_task['title'] == "Updated Title"
        assert updated_task['status'] == "completed"
        assert updated_task['id'] == task_id
    
    def test_update_task_partial(self):
        """Test updating only some fields of a task."""
        created_task = TaskService.create_task(
            title="Original",
            description="Original Desc"
        )
        task_id = created_task['id']
        
        updated_task = TaskService.update_task(
            task_id=task_id,
            status="completed"
        )
        
        assert updated_task['status'] == "completed"
        assert updated_task['title'] == "Original"  # Unchanged
        assert updated_task['description'] == "Original Desc"  # Unchanged
    
    def test_update_task_not_found(self):
        """Test updating a non-existent task."""
        result = TaskService.update_task(task_id=99999, title="New Title")
        assert result is None
    
    def test_update_task_invalid_status(self):
        """Test updating task with invalid status."""
        created_task = TaskService.create_task(title="Test")
        
        with pytest.raises(ValueError, match="Status must be"):
            TaskService.update_task(
                task_id=created_task['id'],
                status="invalid"
            )
    
    def test_delete_task_success(self):
        """Test successful task deletion."""
        created_task = TaskService.create_task(title="To Delete")
        task_id = created_task['id']
        
        result = TaskService.delete_task(task_id)
        assert result is True
        
        # Verify task is deleted
        retrieved_task = TaskService.get_task_by_id(task_id)
        assert retrieved_task is None
    
    def test_delete_task_not_found(self):
        """Test deleting a non-existent task."""
        result = TaskService.delete_task(99999)
        assert result is False


class TestTaskAPI:
    # Tests for the API endpoints
    
    def test_create_task_api_success(self, client):
        """Test successful task creation via API."""
        data = {
            "title": "API Test Task",
            "description": "API Description",
            "due_date": "2026-03-20",
            "status": "pending"
        }
        
        response = client.post(
            '/api/tasks/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = json.loads(response.content)
        assert result['success'] is True
        assert result['data']['title'] == "API Test Task"
        assert 'id' in result['data']
    
    def test_create_task_api_invalid_json(self, client):
        """Test API with invalid JSON."""
        response = client.post(
            '/api/tasks/',
            data="invalid json",
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert result['success'] is False
    
    def test_create_task_api_missing_title(self, client):
        """Test API with missing required field."""
        data = {
            "description": "No title"
        }
        
        response = client.post(
            '/api/tasks/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.content)
        assert result['success'] is False
    
    def test_get_all_tasks_api_empty(self, client):
        """Test getting all tasks when database is empty."""
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True
        assert result['data'] == []
        assert result['count'] == 0
    
    def test_get_all_tasks_api_with_data(self, client):
        """Test getting all tasks with existing data."""
        # Create tasks via service
        TaskService.create_task(title="Task 1")
        TaskService.create_task(title="Task 2")
        
        response = client.get('/api/tasks')
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True
        assert len(result['data']) == 2
        assert result['count'] == 2
    
    def test_get_task_api_success(self, client):
        """Test getting a specific task by ID."""
        created_task = TaskService.create_task(title="Get Me")
        task_id = created_task['id']
        
        response = client.get(f'/api/tasks/{task_id}/')
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True
        assert result['data']['id'] == task_id
        assert result['data']['title'] == "Get Me"
    
    def test_get_task_api_not_found(self, client):
        """Test getting a non-existent task."""
        response = client.get('/api/tasks/99999/')
        
        assert response.status_code == 404
        result = json.loads(response.content)
        assert result['success'] is False
        assert 'not found' in result['message'].lower()
    
    def test_update_task_api_success(self, client):
        """Test successful task update via API."""
        created_task = TaskService.create_task(title="Original")
        task_id = created_task['id']
        
        data = {
            "title": "Updated",
            "status": "completed"
        }
        
        response = client.put(
            f'/api/tasks/{task_id}/update/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True
        assert result['data']['title'] == "Updated"
        assert result['data']['status'] == "completed"
    
    def test_update_task_api_not_found(self, client):
        """Test updating a non-existent task."""
        data = {"title": "Updated"}
        
        response = client.put(
            '/api/tasks/99999/update/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        result = json.loads(response.content)
        assert result['success'] is False
    
    def test_delete_task_api_success(self, client):
        """Test successful task deletion via API."""
        created_task = TaskService.create_task(title="To Delete")
        task_id = created_task['id']
        
        response = client.delete(f'/api/tasks/{task_id}/delete/')
        
        assert response.status_code == 200
        result = json.loads(response.content)
        assert result['success'] is True
        
        # Verify task is deleted
        get_response = client.get(f'/api/tasks/{task_id}/')
        assert get_response.status_code == 404
    
    def test_delete_task_api_not_found(self, client):
        """Test deleting a non-existent task."""
        response = client.delete('/api/tasks/99999/delete/')
        
        assert response.status_code == 404
        result = json.loads(response.content)
        assert result['success'] is False
    
    def test_task_list_view(self, client):
        """Test that task list view renders successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'task-list-container' in response.content.decode()
    
    def test_add_task_view(self, client):
        """Test that add task view renders successfully."""
        response = client.get('/add/')
        assert response.status_code == 200
        assert 'add-task-form' in response.content.decode()


class TestDatabaseOperations:
    # Tests for database setup and initialization
    
    def test_database_initialization(self):
        # Make sure the table gets created properly
        initialize_database()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the tasks table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tasks'
        """)
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'tasks'
        
        conn.close()
    
    def test_database_index_creation(self):
        # Verify that the status index gets created
        initialize_database()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the index exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_tasks_status'
        """)
        
        result = cursor.fetchone()
        assert result is not None
        
        conn.close()
