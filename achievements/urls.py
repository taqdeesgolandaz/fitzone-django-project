from django.urls import path
from . import views

app_name = 'achievements'

urlpatterns = [
    path('', views.achievements_dashboard, name='dashboard'),
    path('badge/<int:badge_id>/', views.badge_detail, name='badge_detail'),
]