from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe'),
    path('admin/newsletter/', views.newsletter_subscribers, name='newsletter_subscribers'),
    path('admin/newsletter/export/', views.export_subscribers, name='export_subscribers'),
    path('admin/newsletter/delete/<int:subscriber_id>/', views.delete_subscriber, name='delete_subscriber'),
]