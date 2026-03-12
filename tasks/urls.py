# URL routing for the tasks app
# Maps URLs to view functions

from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/tasks/', views.create_task_api, name='create_task_api'),
    path('api/tasks', views.get_all_tasks_api, name='get_all_tasks_api'),
    path('api/tasks/<int:task_id>/', views.get_task_api, name='get_task_api'),
    path('api/tasks/<int:task_id>', views.get_task_api, name='get_task_api_no_slash'),
    path('api/tasks/<int:task_id>/update/', views.update_task_api, name='update_task_api'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task_api, name='delete_task_api'),
    
    # Web pages
    path('', views.task_list_view, name='task_list'),
    path('add/', views.add_task_view, name='add_task'),
]
