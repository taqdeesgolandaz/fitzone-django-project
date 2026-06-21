from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('revenue-report/', views.revenue_report, name='revenue_report'),
    path('user-report/', views.user_report, name='user_report'),
    path('membership-report/', views.membership_report, name='membership_report'),
    path('membership-report/cancel/<int:membership_id>/', views.cancel_membership, name='cancel_membership'),
    path('trainer-report/', views.trainer_report, name='trainer_report'),
    path('workout-report/', views.workout_report, name='workout_report'),
]