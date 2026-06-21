from django.contrib import admin
from .models import FitnessProgress, UserFitnessGoal, WorkoutLog

@admin.register(FitnessProgress)
class FitnessProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_recorded', 'weight', 'bmi', 'body_fat_percentage']
    list_filter = ['date_recorded']
    search_fields = ['user__username']
    list_editable = ['weight']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'date_recorded')
        }),
        ('Body Measurements', {
            'fields': ('weight', 'height', 'bmi', 'body_fat_percentage')
        }),
        ('Body Circumference', {
            'fields': ('chest', 'waist', 'hips', 'biceps', 'thighs')
        }),
        ('Health Metrics', {
            'fields': ('resting_heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    readonly_fields = ['bmi', 'created_at', 'updated_at']


@admin.register(UserFitnessGoal)
class UserFitnessGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_type', 'target_weight', 'target_date', 'is_active', 'achieved']
    list_filter = ['goal_type', 'is_active', 'achieved']
    search_fields = ['user__username']
    list_editable = ['is_active']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'goal_type')
        }),
        ('Target Goals', {
            'fields': ('target_weight', 'target_body_fat', 'target_date')
        }),
        ('Weekly Targets', {
            'fields': ('weekly_workout_goal', 'weekly_calorie_goal')
        }),
        ('Status', {
            'fields': ('is_active', 'achieved', 'achieved_date')
        }),
    )


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'duration_minutes', 'calories_burned', 'felt_difficulty']
    list_filter = ['date', 'felt_difficulty']
    search_fields = ['user__username', 'notes']
    list_editable = ['duration_minutes', 'calories_burned']
    
    fieldsets = (
        ('Workout Information', {
            'fields': ('user', 'date', 'workout_plan')
        }),
        ('Workout Metrics', {
            'fields': ('duration_minutes', 'calories_burned', 'felt_difficulty')
        }),
        ('Details', {
            'fields': ('exercises_completed', 'notes')
        }),
    )