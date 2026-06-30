from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import MembershipPlan, UserMembership

def cancel_membership(modeladmin, request, queryset):
    """Admin action to cancel user memberships"""
    for membership in queryset:
        membership.status = 'cancelled'
        membership.save()
        
        # Reset user's membership flags only if no other active memberships exist
        user = membership.user
        
        # Check if user has any other active memberships
        other_active = UserMembership.objects.filter(
            user=user,
            status='active',
            end_date__gt=timezone.now()
        ).exclude(id=membership.id).exists()
        
        if not other_active:
            # No other active memberships, reset user state
            user.membership_active = False
            user.current_membership = None
            user.membership_expiry = None
            user.save()
    
    modeladmin.message_user(request, f'{queryset.count()} membership(s) cancelled successfully. Users can now purchase a new plan.')

cancel_membership.short_description = 'Cancel selected memberships and allow users to purchase new plans'


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'duration', 'price', 'is_active', 'is_popular']
    list_filter = ['plan_type', 'duration', 'is_active', 'is_popular']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active', 'is_popular']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'duration', 'price', 'description')
        }),
        ('Features', {
            'fields': ('features', 'workout_plan_included', 'diet_plan_included', 'personal_trainer')
        }),
        ('Status', {
            'fields': ('is_active', 'is_popular')
        }),
    )

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'status_badge', 'amount_paid']
    list_filter = ['status', 'plan']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['start_date', 'created_at']
    actions = [cancel_membership]
    
    def status_badge(self, obj):
        """Display status with color-coded badge"""
        colors = {
            'active': '#00D09C',
            'expired': '#F5A623',
            'cancelled': '#f87171',
        }
        color = colors.get(obj.status, '#A0A0A0')
        return format_html(
            '<span style="color: {}; font-weight: bold;">✓ {}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
