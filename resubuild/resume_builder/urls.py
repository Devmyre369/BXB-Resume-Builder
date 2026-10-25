
from django.urls import path
from . import views

app_name = 'resume_builder'

urlpatterns = [
    path('', views.home, name='home'),
    path('editor/', views.editor, name='editor'),

    # Resume Intelligence API
    path(
        'api/analyze/',
        views.analyze_resume_api,
        name='analyze_resume_api',
    ),
]
