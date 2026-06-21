from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.workout_list, name='list'),
    path('plan/<int:plan_id>/', views.workout_detail, name='detail'),
    path('start/<int:plan_id>/', views.start_workout, name='start_workout'),
    path('track/<int:progress_id>/', views.track_workout, name='track_workout'),
    path('my-progress/', views.my_progress, name='my_progress'),  # Already protected
]