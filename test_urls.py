"""
Test URL configuration without Swagger dependencies.
"""

from django.urls import path, include

urlpatterns = [
    # Include URLs from the tasks app (without Swagger)
    path('', include('tasks.urls')),
]
