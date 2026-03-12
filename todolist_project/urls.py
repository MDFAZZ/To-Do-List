# Main URL configuration for the project

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings

# Try to set up Swagger, but it's optional
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    schema_view = None

urlpatterns = [
    # Include all the task URLs
    path('', include('tasks.urls')),
]

# Add Swagger docs if available
if SWAGGER_AVAILABLE:
    try:
        # Get permissions class if DRF is available
        try:
            from rest_framework.permissions import AllowAny
            permission_classes = (AllowAny,)
        except ImportError:
            permission_classes = ()
        
        # Set up the schema view for Swagger
        schema_view = get_schema_view(
            openapi.Info(
                title="To-Do List API",
                default_version='v1',
                description="""
                RESTful API for managing tasks in the To-Do List application.
                
                ## API Endpoints:
                
                - **POST /api/tasks/** - Create a new task
                - **GET /api/tasks** - Get all tasks  
                - **GET /api/tasks/{id}/** - Get a specific task
                - **PUT /api/tasks/{id}/update/** - Update a task
                - **DELETE /api/tasks/{id}/delete/** - Delete a task
                
                All endpoints return JSON responses and follow RESTful principles.
                """,
                terms_of_service="https://www.pelocal.com/terms/",
                contact=openapi.Contact(email="hr@pelocal.com"),
                license=openapi.License(name="Proprietary"),
            ),
            public=True,
            permission_classes=permission_classes,
            patterns=[path('api/', include('tasks.urls'))],
        )
        
        # Swagger UI URLs
        urlpatterns = [
            re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
            path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        ] + urlpatterns
    except (Exception, RuntimeError) as e:
        # Swagger failed to initialize - might be missing dependencies
        # Just continue without it
        import logging
        logger = logging.getLogger('tasks')
        logger.warning(f"Swagger documentation not available: {str(e)}")
        SWAGGER_AVAILABLE = False

# Fallback if Swagger isn't available
if not SWAGGER_AVAILABLE:
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    @require_http_methods(["GET"])
    def swagger_unavailable(request):
        # Return a helpful message when Swagger isn't working
        return JsonResponse({
            'message': 'Swagger documentation is not available',
            'reason': 'Swagger requires Python 3.11 or 3.12 with setuptools, or Docker environment',
            'alternative': 'See API_DOCUMENTATION.md for complete API documentation',
            'endpoints': {
                'api': '/api/tasks',
                'web': '/',
            },
            'note': 'All API endpoints are fully functional. Swagger is optional documentation only.'
        }, status=503)
    
    # Add placeholder URLs
    urlpatterns = [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', swagger_unavailable, name='schema-json'),
        path('swagger/', swagger_unavailable, name='schema-swagger-ui'),
        path('redoc/', swagger_unavailable, name='schema-redoc'),
    ] + urlpatterns
