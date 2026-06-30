from django.contrib import admin
from .models import Trainer, TrainerSession, TrainerReview

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['position', 'full_name', 'specialization', 'experience_level', 'monthly_rate', 'is_available', 'is_verified', 'average_rating']
    list_filter = ['specialization', 'experience_level', 'is_available', 'is_verified']
    search_fields = ['full_name', 'email', 'bio']
    list_editable = ['position', 'is_available', 'is_verified', 'monthly_rate']
    ordering = ['position']
    actions = ['move_up', 'move_down']
    # Make `full_name` clickable; `position` is editable so it cannot be the link
    list_display_links = ('full_name',)
    
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

    def move_up(self, request, queryset):
        """Move selected trainers up in ordering (swap with previous)."""
        try:
            count = 0
            for obj in queryset.order_by('position'):
                neighbor = Trainer.objects.filter(position__lt=obj.position).order_by('-position').first()
                if neighbor:
                    obj.position, neighbor.position = neighbor.position, obj.position
                    obj.save(update_fields=['position'])
                    neighbor.save(update_fields=['position'])
                    count += 1
            if count > 0:
                self.message_user(request, f"{count} trainer(s) moved up successfully")
            else:
                self.message_user(request, "No trainers could be moved up (already at top)")
        except Exception as e:
            self.message_user(request, f"Error moving trainers up: {str(e)}", level='error')
    move_up.short_description = 'Move selected trainers up'

    def move_down(self, request, queryset):
        """Move selected trainers down in ordering (swap with next)."""
        try:
            count = 0
            for obj in queryset.order_by('-position'):
                neighbor = Trainer.objects.filter(position__gt=obj.position).order_by('position').first()
                if neighbor:
                    obj.position, neighbor.position = neighbor.position, obj.position
                    obj.save(update_fields=['position'])
                    neighbor.save(update_fields=['position'])
                    count += 1
            if count > 0:
                self.message_user(request, f"{count} trainer(s) moved down successfully")
            else:
                self.message_user(request, "No trainers could be moved down (already at bottom)")
        except Exception as e:
            self.message_user(request, f"Error moving trainers down: {str(e)}", level='error')
    move_down.short_description = 'Move selected trainers down'

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