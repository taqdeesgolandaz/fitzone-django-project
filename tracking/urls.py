from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('', views.tracking_dashboard, name='dashboard'),
    path('add-progress/', views.add_progress, name='add_progress'),
    path('edit-progress/<int:progress_id>/', views.edit_progress, name='edit_progress'),
    path('delete-progress/<int:progress_id>/', views.delete_progress, name='delete_progress'),
    path('set-goal/', views.set_goal, name='set_goal'),
    path('bmi-calculator/', views.bmi_calculator, name='bmi_calculator'),
    path('workout-log/', views.workout_log, name='workout_log'),
]