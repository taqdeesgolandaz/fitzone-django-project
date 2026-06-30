from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import WorkoutCategory, Exercise, WorkoutPlan, WorkoutPlanExercise, UserWorkoutProgress

class WorkoutPlanExerciseInline(admin.TabularInline):
    """Inline form for exercises in workout plan"""
    model = WorkoutPlanExercise
    extra = 1
    fields = ['exercise', 'order', 'sets', 'reps', 'rest_seconds']
    autocomplete_fields = ['exercise']


@admin.register(WorkoutCategory)
class WorkoutCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'body_part', 'category', 'duration_minutes', 'calories_burn', 'is_active']
    list_filter = ['body_part', 'category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'day_of_week', 'duration_weeks', 'exercise_count', 'is_active']
    list_filter = ['difficulty', 'day_of_week', 'is_active']
    search_fields = ['name', 'description']
    inlines = [WorkoutPlanExerciseInline]  # Use inline instead of filter_horizontal
    
    def exercise_count(self, obj):
        try:
            return getattr(obj.exercises, 'count', lambda: 0)()
        except Exception:
            return 0
    exercise_count.short_description = 'Exercises'


@admin.register(WorkoutPlanExercise)
class WorkoutPlanExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout_plan', 'exercise', 'order', 'sets', 'reps']
    list_filter = ['workout_plan__difficulty', 'workout_plan__day_of_week']
    search_fields = ['workout_plan__name', 'exercise__name']


@admin.register(UserWorkoutProgress)
class UserWorkoutProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_plan', 'scheduled_date', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['user__username', 'workout_plan__name']
    readonly_fields = ['created_at', 'updated_at']