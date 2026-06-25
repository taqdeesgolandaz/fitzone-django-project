from django.contrib import admin
from django.urls import path, include
from notifications import views as notifications_views
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import login_view

urlpatterns = [
    path('admin/notifications/', notifications_views.admin_notifications, name='admin_notifications_fallback'),
    path('admin/notifications/open/<int:notification_id>/', notifications_views.admin_open_notification, name='admin_notification_open'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('', include('accounts.urls')),
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('accounts/', include('allauth.urls')),
    path('membership/', include(('membership.urls', 'membership'), namespace='membership')),
    path('payments/', include('payments.urls')),  # This line is critical
    path('workouts/', include('workouts.urls')),  # Add this line
    path('diet/', include('diet.urls')),  # Add this line
    path('trainers/', include('trainers.urls')),  # Add this line
    path('tracking/', include('tracking.urls')),  # Add this line
    path('admin-dashboard/', include('admin_dashboard.urls')),  # Add this line
    path('notifications/', include('notifications.urls')),
    path('achievements/', include('achievements.urls')),
    path('support/', include('support.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)