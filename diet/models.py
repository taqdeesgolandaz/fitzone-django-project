from django.db import models
from django.conf import settings
from django.utils import timezone

class DietCategory(models.Model):
    """Diet plan categories"""
    
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-apple-alt')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Diet Categories'


class Meal(models.Model):
    """Individual meals"""
    
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    
    # Nutrition information
    calories = models.IntegerField(default=0)
    protein = models.IntegerField(default=0, help_text="Grams")
    carbohydrates = models.IntegerField(default=0, help_text="Grams")
    fats = models.IntegerField(default=0, help_text="Grams")
    fiber = models.IntegerField(default=0, help_text="Grams")
    
    # Ingredients and instructions
    ingredients = models.TextField(help_text="List of ingredients, one per line")
    instructions = models.TextField(help_text="Cooking instructions")
    
    # Image
    image = models.ImageField(upload_to='meal_images/', blank=True, null=True)
    
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_meal_type_display()})"


class DietPlan(models.Model):
    """Daily diet plans"""
    
    DIET_GOALS = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
    ]
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    diet_goal = models.CharField(max_length=20, choices=DIET_GOALS)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    
    # Meals for this plan
    breakfast = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='breakfast_plans')
    lunch = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='lunch_plans')
    dinner = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='dinner_plans')
    snack1 = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='snack1_plans')
    snack2 = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name='snack2_plans')
    
    # Daily totals
    total_calories = models.IntegerField(default=0)
    total_protein = models.IntegerField(default=0)
    total_carbs = models.IntegerField(default=0)
    total_fats = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_diet_goal_display()} ({self.get_day_of_week_display()})"
    
    def save(self, *args, **kwargs):
        # Calculate totals
        self.total_calories = 0
        self.total_protein = 0
        self.total_carbs = 0
        self.total_fats = 0
        
        for meal in [self.breakfast, self.lunch, self.dinner, self.snack1, self.snack2]:
            if meal:
                self.total_calories += meal.calories
                self.total_protein += meal.protein
                self.total_carbs += meal.carbohydrates
                self.total_fats += meal.fats
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['diet_goal', 'day_of_week']


class UserDietProgress(models.Model):
    """Track user's meal completion"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diet_progress')
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True, blank=True)
    scheduled_date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=Meal.MEAL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} - {self.scheduled_date}"
    
    class Meta:
        unique_together = ['user', 'diet_plan', 'meal_type', 'scheduled_date']
        ordering = ['-scheduled_date']