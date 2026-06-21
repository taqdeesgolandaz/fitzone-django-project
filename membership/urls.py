from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('purchase/<int:plan_id>/', views.purchase_plan, name='purchase'),
    path('my-membership/', views.my_membership_view, name='my_membership'),
]