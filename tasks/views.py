# API views for all the task endpoints
# All custom function-based views (no generic viewsets as per requirements)

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Using @api_view decorator from DRF just for Swagger compatibility
# It's not a viewset, just a decorator for function-based views
try:
    from rest_framework.decorators import api_view
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False
    # Fallback if DRF isn't available
    def api_view(http_method_names=None):
        def decorator(func):
            return func
        return decorator

# Swagger is optional - app works fine without it
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
    SWAGGER_AVAILABLE = True
except ImportError:
    # Mock decorator if Swagger isn't installed
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    # Mock classes for when Swagger isn't available
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
    # Make sure the database table exists before handling requests
    # Called at the start of each view
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
    # POST /api/tasks/ - Creates a new task
    # Expects JSON with title (required), description, due_date, status (optional)
    initialize_db_if_needed()
    
    try:
        # Parse the JSON body
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in create task request")
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format',
                'error': 'Request body must be valid JSON'
            }, status=400)
        
        # Pull out the fields
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status', 'pending')
        
        # Create it via the service layer
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
    # GET /api/tasks - Returns all tasks
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
    # GET /api/tasks/{id}/ - Gets a single task by ID
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
    # PUT/PATCH /api/tasks/{id}/update/ - Updates a task
    # All fields in the JSON body are optional - only provided ones get updated
    initialize_db_if_needed()
    
    try:
        task_id = int(task_id)
        
        # Parse JSON
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in update task request")
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format',
                'error': 'Request body must be valid JSON'
            }, status=400)
        
        # Get the fields to update (all optional)
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status')
        
        # Update via service
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
    # DELETE /api/tasks/{id}/delete/ - Deletes a task
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
    # Web view - renders the main task list page
    # The template uses JS to fetch tasks from the API
    initialize_db_if_needed()
    from django.shortcuts import render
    return render(request, 'tasks/list.html')


def add_task_view(request):
    # Web view - renders the add task form page
    # Form submission is handled by JS calling the API
    initialize_db_if_needed()
    from django.shortcuts import render
    return render(request, 'tasks/add.html')
