"""
URL configuration for the tasks application.

This module defines all the URL routes for:
- API endpoints (RESTful)
- Web interface views (templates)
"""

from django.urls import path
from . import views

# URL patterns for the tasks application
urlpatterns = [
    # API Endpoints (RESTful)
    path('api/tasks/', views.create_task_api, name='create_task_api'),
    path('api/tasks', views.get_all_tasks_api, name='get_all_tasks_api'),
    path('api/tasks/<int:task_id>/', views.get_task_api, name='get_task_api'),
    path('api/tasks/<int:task_id>', views.get_task_api, name='get_task_api_no_slash'),
    path('api/tasks/<int:task_id>/update/', views.update_task_api, name='update_task_api'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task_api, name='delete_task_api'),
    
    # Web Interface Views (Templates)
    path('', views.task_list_view, name='task_list'),
    path('add/', views.add_task_view, name='add_task'),
]
