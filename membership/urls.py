from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
    path('purchase/<int:plan_id>/', views.purchase_plan, name='purchase'),
    path('upgrade/<int:plan_id>/', views.upgrade_membership, name='upgrade'),
    path('process-upgrade/', views.process_upgrade, name='process_upgrade'),
    path('my-membership/', views.my_membership_view, name='my_membership'),
]