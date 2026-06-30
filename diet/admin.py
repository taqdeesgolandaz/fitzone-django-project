from django.contrib import admin
from .models import DietCategory, Meal, DietPlan, UserDietProgress

@admin.register(DietCategory)
class DietCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'calories', 'protein', 'carbohydrates', 'fats']
    list_filter = ['meal_type', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'meal_type', 'image')
        }),
        ('Nutrition Facts', {
            'fields': ('calories', 'protein', 'carbohydrates', 'fats', 'fiber')
        }),
        ('Recipe', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Dietary Preferences', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free')
        }),
    )

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'diet_goal', 'day_of_week', 'total_calories', 'is_active']
    list_filter = ['diet_goal', 'day_of_week', 'is_active']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'diet_goal', 'day_of_week', 'is_active')
        }),
        ('Meals', {
            'fields': ('breakfast', 'lunch', 'dinner', 'snack1', 'snack2')
        }),
        ('Nutrition Summary', {
            'fields': ('total_calories', 'total_protein', 'total_carbs', 'total_fats')
        }),
    )
    readonly_fields = ['total_calories', 'total_protein', 'total_carbs', 'total_fats']

@admin.register(UserDietProgress)
class UserDietProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_meal_name', 'scheduled_date', 'status']
    list_filter = ['status', 'scheduled_date', 'meal_type']
    search_fields = ['user__username']
    
    def get_meal_name(self, obj):
        try:
            meal = getattr(obj, 'meal', None)
            return meal.name if meal else getattr(obj, 'meal_type', 'N/A')
        except Exception:
            return 'N/A'
    get_meal_name.short_description = 'Meal'