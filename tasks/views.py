"""
API views for task management.

This module contains all the API endpoints for CRUD operations on tasks.
All views return JSON responses and handle errors appropriately.
Following the requirement to not use generic viewsets, all views are custom implementations.
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Import DRF api_view decorator to make Swagger work with function-based views
# Note: @api_view is NOT a generic viewset - it's just a decorator for function-based views
try:
    from rest_framework.decorators import api_view
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False
    # Create a no-op decorator if DRF is not available
    def api_view(http_method_names=None):
        def decorator(func):
            return func
        return decorator

# Try to import Swagger, but make it optional for testing
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
    SWAGGER_AVAILABLE = True
except ImportError:
    # Create a no-op decorator if Swagger is not available
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    # Create a mock openapi module with necessary attributes
    class MockSchema:
        def __init__(self, *args, **kwargs):
            pass
    class MockResponse:
        def __init__(self, *args, **kwargs):
            pass
    class MockParameter:
        def __init__(self, *args, **kwargs):
            pass
    class MockItems:
        def __init__(self, *args, **kwargs):
            pass
    class MockOpenAPI:
        Schema = MockSchema
        Response = MockResponse
        Parameter = MockParameter
        Items = MockItems
        TYPE_OBJECT = 'object'
        TYPE_STRING = 'string'
        TYPE_INTEGER = 'integer'
        TYPE_BOOLEAN = 'boolean'
        TYPE_ARRAY = 'array'
        IN_PATH = 'path'
        FORMAT_DATE = 'date'
    openapi = MockOpenAPI()
    SWAGGER_AVAILABLE = False

from .task_service import TaskService
from .database import initialize_database

logger = logging.getLogger('tasks')


def initialize_db_if_needed():
    """
    Initialize database on first request if not already initialized.
    This is a helper function to ensure the database is set up.
    """
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")


@swagger_auto_schema(
    method='post',
    operation_description="Create a new task in the system",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['title'],
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Task title (required)'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Task description (optional)'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Due date in YYYY-MM-DD format (optional)'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['pending', 'completed'], description='Task status (optional, default: pending)'),
        },
    ),
    responses={
        201: openapi.Response(
            description='Task created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'due_date': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                            'updated_at': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                }
            )
        ),
        400: openapi.Response(description='Validation error or invalid JSON'),
        500: openapi.Response(description='Internal server error'),
    },
    tags=['Tasks']
)
@csrf_exempt
@api_view(['POST'])
def create_task_api(request):
    """
    API endpoint to create a new task.
    
    HTTP Method: POST
    Content-Type: application/json
    
    Request Body:
        {
            "title": "string (required)",
            "description": "string (optional)",
            "due_date": "YYYY-MM-DD (optional)",
            "status": "pending|completed (optional, default: pending)"
        }
    
    Response (Success - 201):
        {
            "success": true,
            "message": "Task created successfully",
            "data": {
                "id": 1,
                "title": "Task title",
                "description": "Task description",
                "due_date": "2026-03-15",
                "status": "pending",
                "created_at": "2026-03-10 10:00:00",
                "updated_at": "2026-03-10 10:00:00"
            }
        }
    
    Response (Error - 400):
        {
            "success": false,
            "message": "Error message",
            "error": "Detailed error information"
        }
    """
    initialize_db_if_needed()
    
    try:
        # Parse JSON request body
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in create task request")
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format',
                'error': 'Request body must be valid JSON'
            }, status=400)
        
        # Extract task data
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status', 'pending')
        
        # Create task using service
        task = TaskService.create_task(
            title=title,
            description=description,
            due_date=due_date,
            status=status
        )
        
        logger.info(f"Task created via API: ID {task['id']}")
        return JsonResponse({
            'success': True,
            'message': 'Task created successfully',
            'data': task
        }, status=201)
        
    except ValueError as e:
        logger.warning(f"Validation error in create task: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Validation error',
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in create task API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred while creating the task'
        }, status=500)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all tasks from the system",
    responses={
        200: openapi.Response(
            description='Tasks retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        500: openapi.Response(description='Internal server error'),
    },
    tags=['Tasks']
)
@api_view(['GET'])
def get_all_tasks_api(request):
    """
    API endpoint to retrieve all tasks.
    
    HTTP Method: GET
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Tasks retrieved successfully",
            "data": [
                {
                    "id": 1,
                    "title": "Task title",
                    "description": "Task description",
                    "due_date": "2026-03-15",
                    "status": "pending",
                    "created_at": "2026-03-10 10:00:00",
                    "updated_at": "2026-03-10 10:00:00"
                },
                ...
            ],
            "count": 2
        }
    
    Response (Error - 500):
        {
            "success": false,
            "message": "Internal server error",
            "error": "Error details"
        }
    """
    initialize_db_if_needed()
    
    try:
        tasks = TaskService.get_all_tasks()
        
        logger.debug(f"Retrieved {len(tasks)} tasks via API")
        return JsonResponse({
            'success': True,
            'message': 'Tasks retrieved successfully',
            'data': tasks,
            'count': len(tasks)
        }, status=200)
        
    except Exception as e:
        logger.error(f"Unexpected error in get all tasks API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred while retrieving tasks'
        }, status=500)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a specific task by its ID",
    manual_parameters=[
        openapi.Parameter('task_id', openapi.IN_PATH, description="Task ID", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={
        200: openapi.Response(
            description='Task retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        404: openapi.Response(description='Task not found'),
        400: openapi.Response(description='Invalid task ID'),
        500: openapi.Response(description='Internal server error'),
    },
    tags=['Tasks']
)
@api_view(['GET'])
def get_task_api(request, task_id):
    """
    API endpoint to retrieve a specific task by ID.
    
    HTTP Method: GET
    URL Parameter: task_id (integer)
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Task retrieved successfully",
            "data": {
                "id": 1,
                "title": "Task title",
                "description": "Task description",
                "due_date": "2026-03-15",
                "status": "pending",
                "created_at": "2026-03-10 10:00:00",
                "updated_at": "2026-03-10 10:00:00"
            }
        }
    
    Response (Not Found - 404):
        {
            "success": false,
            "message": "Task not found",
            "error": "Task with the specified ID does not exist"
        }
    """
    initialize_db_if_needed()
    
    try:
        task_id = int(task_id)
        task = TaskService.get_task_by_id(task_id)
        
        if task:
            logger.debug(f"Retrieved task {task_id} via API")
            return JsonResponse({
                'success': True,
                'message': 'Task retrieved successfully',
                'data': task
            }, status=200)
        else:
            logger.warning(f"Task {task_id} not found via API")
            return JsonResponse({
                'success': False,
                'message': 'Task not found',
                'error': f'Task with ID {task_id} does not exist'
            }, status=404)
            
    except ValueError:
        logger.warning(f"Invalid task_id in get task API: {task_id}")
        return JsonResponse({
            'success': False,
            'message': 'Invalid task ID',
            'error': 'Task ID must be a valid integer'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in get task API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred while retrieving the task'
        }, status=500)


@swagger_auto_schema(
    method='put',
    operation_description="Update an existing task. All fields are optional - only provided fields will be updated.",
    manual_parameters=[
        openapi.Parameter('task_id', openapi.IN_PATH, description="Task ID", type=openapi.TYPE_INTEGER, required=True),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Task title (optional)'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Task description (optional)'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Due date in YYYY-MM-DD format (optional)'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['pending', 'completed'], description='Task status (optional)'),
        },
    ),
    responses={
        200: openapi.Response(description='Task updated successfully'),
        404: openapi.Response(description='Task not found'),
        400: openapi.Response(description='Validation error'),
        500: openapi.Response(description='Internal server error'),
    },
    tags=['Tasks']
)
@csrf_exempt
@api_view(['PUT', 'PATCH'])
def update_task_api(request, task_id):
    """
    API endpoint to update an existing task.
    
    HTTP Method: PUT or PATCH
    URL Parameter: task_id (integer)
    Content-Type: application/json
    
    Request Body (all fields optional):
        {
            "title": "string (optional)",
            "description": "string (optional)",
            "due_date": "YYYY-MM-DD (optional)",
            "status": "pending|completed (optional)"
        }
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Task updated successfully",
            "data": {
                "id": 1,
                "title": "Updated title",
                "description": "Updated description",
                "due_date": "2026-03-20",
                "status": "completed",
                "created_at": "2026-03-10 10:00:00",
                "updated_at": "2026-03-10 11:00:00"
            }
        }
    
    Response (Not Found - 404):
        {
            "success": false,
            "message": "Task not found",
            "error": "Task with the specified ID does not exist"
        }
    """
    initialize_db_if_needed()
    
    try:
        task_id = int(task_id)
        
        # Parse JSON request body
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in update task request")
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format',
                'error': 'Request body must be valid JSON'
            }, status=400)
        
        # Extract update data (all optional)
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status')
        
        # Update task using service
        task = TaskService.update_task(
            task_id=task_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status
        )
        
        if task:
            logger.info(f"Task {task_id} updated via API")
            return JsonResponse({
                'success': True,
                'message': 'Task updated successfully',
                'data': task
            }, status=200)
        else:
            logger.warning(f"Task {task_id} not found for update via API")
            return JsonResponse({
                'success': False,
                'message': 'Task not found',
                'error': f'Task with ID {task_id} does not exist'
            }, status=404)
            
    except ValueError as e:
        if isinstance(e, (ValueError,)) and 'Task ID' in str(e):
            logger.warning(f"Invalid task_id in update task API: {task_id}")
            return JsonResponse({
                'success': False,
                'message': 'Invalid task ID',
                'error': 'Task ID must be a valid integer'
            }, status=400)
        else:
            logger.warning(f"Validation error in update task: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Validation error',
                'error': str(e)
            }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in update task API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred while updating the task'
        }, status=500)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete a task from the system",
    manual_parameters=[
        openapi.Parameter('task_id', openapi.IN_PATH, description="Task ID", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={
        200: openapi.Response(description='Task deleted successfully'),
        404: openapi.Response(description='Task not found'),
        400: openapi.Response(description='Invalid task ID'),
        500: openapi.Response(description='Internal server error'),
    },
    tags=['Tasks']
)
@csrf_exempt
@api_view(['DELETE'])
def delete_task_api(request, task_id):
    """
    API endpoint to delete a task.
    
    HTTP Method: DELETE
    URL Parameter: task_id (integer)
    
    Response (Success - 200):
        {
            "success": true,
            "message": "Task deleted successfully"
        }
    
    Response (Not Found - 404):
        {
            "success": false,
            "message": "Task not found",
            "error": "Task with the specified ID does not exist"
        }
    """
    initialize_db_if_needed()
    
    try:
        task_id = int(task_id)
        deleted = TaskService.delete_task(task_id)
        
        if deleted:
            logger.info(f"Task {task_id} deleted via API")
            return JsonResponse({
                'success': True,
                'message': 'Task deleted successfully'
            }, status=200)
        else:
            logger.warning(f"Task {task_id} not found for deletion via API")
            return JsonResponse({
                'success': False,
                'message': 'Task not found',
                'error': f'Task with ID {task_id} does not exist'
            }, status=404)
            
    except ValueError:
        logger.warning(f"Invalid task_id in delete task API: {task_id}")
        return JsonResponse({
            'success': False,
            'message': 'Invalid task ID',
            'error': 'Task ID must be a valid integer'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in delete task API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred while deleting the task'
        }, status=500)


def task_list_view(request):
    """
    Web interface view to display the list of tasks.
    
    This view renders the HTML template for displaying all tasks.
    The template uses JavaScript to fetch tasks from the API endpoint.
    """
    initialize_db_if_needed()
    from django.shortcuts import render
    return render(request, 'tasks/list.html')


def add_task_view(request):
    """
    Web interface view to display the form for adding a new task.
    
    This view renders the HTML template for adding tasks.
    The template uses JavaScript to submit tasks to the API endpoint.
    """
    initialize_db_if_needed()
    from django.shortcuts import render
    return render(request, 'tasks/add.html')
