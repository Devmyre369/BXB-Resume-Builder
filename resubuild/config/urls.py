"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from resume_builder.views import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resume_builder.urls')),
    path('service-worker.js', service_worker, name='service_worker'),
]
