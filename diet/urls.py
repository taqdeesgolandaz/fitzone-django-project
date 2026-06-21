from django.urls import path
from . import views

app_name = 'diet'

urlpatterns = [
    path('', views.diet_list, name='list'),
    path('plan/<int:plan_id>/', views.diet_detail, name='detail'),
    path('track/<int:progress_id>/', views.track_meal, name='track'),
    path('my-progress/', views.my_diet_progress, name='my_progress'),
    path('shopping-list/', views.shopping_list, name='shopping_list'),
]