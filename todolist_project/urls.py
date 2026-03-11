"""
URL configuration for todolist_project.

This module defines the URL routing for the entire application.
All API endpoints and web interface routes are configured here.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings

# Try to import Swagger, but make it optional
try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    schema_view = None

urlpatterns = [
    # Include URLs from the tasks app
    path('', include('tasks.urls')),
]

# Add Swagger URLs only if available
if SWAGGER_AVAILABLE:
    try:
        # Try to import DRF permissions, but make it optional
        try:
            from rest_framework.permissions import AllowAny
            permission_classes = (AllowAny,)
        except ImportError:
            # DRF not available, use empty tuple
            permission_classes = ()
        
        # Create schema view with manual patterns to ensure function-based views are discovered
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
            permission_classes=permission_classes,  # Allow access without authentication
            patterns=[path('api/', include('tasks.urls'))],  # Include API patterns for discovery
        )
        
        # Swagger/OpenAPI Documentation URLs
        urlpatterns = [
            re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
            path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        ] + urlpatterns
    except (Exception, RuntimeError) as e:
        # If Swagger fails to initialize (e.g., missing auth app, pkg_resources, etc.)
        # Continue without it and use fallback views
        import logging
        logger = logging.getLogger('tasks')
        logger.warning(f"Swagger documentation not available: {str(e)}")
        SWAGGER_AVAILABLE = False  # Mark as unavailable for fallback
# Add fallback views if Swagger is not available
if not SWAGGER_AVAILABLE:
    # Swagger not available - add helpful message views
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    @require_http_methods(["GET"])
    def swagger_unavailable(request):
        """Return a helpful message when Swagger is not available."""
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
    
    # Add placeholder URLs that return helpful messages
    urlpatterns = [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', swagger_unavailable, name='schema-json'),
        path('swagger/', swagger_unavailable, name='schema-swagger-ui'),
        path('redoc/', swagger_unavailable, name='schema-redoc'),
    ] + urlpatterns
