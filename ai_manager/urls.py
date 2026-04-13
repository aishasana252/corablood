from django.urls import path
from . import views

app_name = 'ai_manager'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
]
