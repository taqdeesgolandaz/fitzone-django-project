from django.contrib import admin
from .models import Trainer, TrainerSession, TrainerReview

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'experience_level', 'monthly_rate', 'is_available', 'is_verified', 'average_rating']
    list_filter = ['specialization', 'experience_level', 'is_available', 'is_verified']
    search_fields = ['full_name', 'email', 'bio']
    list_editable = ['is_available', 'is_verified', 'monthly_rate']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'email', 'phone', 'profile_picture')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'experience_level', 'years_of_experience', 'bio', 'qualifications', 'achievements')
        }),
        ('Pricing & Availability', {
            'fields': ('monthly_rate', 'availability', 'is_available', 'is_verified', 'is_featured')
        }),
        ('Ratings', {
            'fields': ('total_ratings', 'average_rating')
        }),
    )

@admin.register(TrainerSession)
class TrainerSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'trainer', 'session_date', 'session_time', 'status', 'amount']
    list_filter = ['status', 'session_type', 'session_date']
    search_fields = ['user__username', 'trainer__full_name']
    list_editable = ['status']
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'trainer', 'session_type', 'session_date', 'session_time', 'duration_minutes', 'amount')
        }),
        ('Status & Notes', {
            'fields': ('status', 'user_notes', 'trainer_notes', 'meeting_link')
        }),
    )

@admin.register(TrainerReview)
class TrainerReviewAdmin(admin.ModelAdmin):
    list_display = ['trainer', 'user', 'rating', 'review_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['trainer__full_name', 'user__username']
    
    def review_preview(self, obj):
        return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
    review_preview.short_description = 'Review'