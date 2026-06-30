from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('revenue-report/', views.revenue_report, name='revenue_report'),
    path('user-report/', views.user_report, name='user_report'),
    path('user-details/<int:user_id>/', views.user_details_view, name='user_details'),
    path('user-deactivate/<int:user_id>/', views.deactivate_user_view, name='deactivate_user'),
    path('user-reactivate/<int:user_id>/', views.reactivate_user_view, name='reactivate_user'),
    path('user-delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('user-confirm-delete/<int:user_id>/', views.confirm_delete_user_view, name='confirm_delete_user'),
    path('recreate-user/<int:audit_id>/', views.recreate_user_view, name='recreate_user'),
    path('user-edit-email/<int:user_id>/', views.edit_user_email, name='edit_user_email'),
    path('membership-report/', views.membership_report, name='membership_report'),
    path('membership-report/cancel/<int:membership_id>/', views.cancel_membership, name='cancel_membership'),
    path('member-details/<int:user_id>/', views.member_details, name='member_details'),
    path('trainer-report/', views.trainer_report, name='trainer_report'),
    path('workout-report/', views.workout_report, name='workout_report'),
]