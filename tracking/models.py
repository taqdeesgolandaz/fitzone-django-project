from django.db import models
from django.conf import settings
from django.utils import timezone

class FitnessProgress(models.Model):
    """Track user's fitness metrics over time"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fitness_progress')
    
    # Body measurements
    weight = models.FloatField(help_text="Weight in kg")
    height = models.FloatField(help_text="Height in cm", blank=True, null=True)
    bmi = models.FloatField(blank=True, null=True)
    body_fat_percentage = models.FloatField(blank=True, null=True, help_text="Body fat percentage")
    
    # Additional metrics
    chest = models.FloatField(blank=True, null=True, help_text="Chest measurement in cm")
    waist = models.FloatField(blank=True, null=True, help_text="Waist measurement in cm")
    hips = models.FloatField(blank=True, null=True, help_text="Hips measurement in cm")
    biceps = models.FloatField(blank=True, null=True, help_text="Biceps measurement in cm")
    thighs = models.FloatField(blank=True, null=True, help_text="Thighs measurement in cm")
    
    # Fitness metrics
    resting_heart_rate = models.IntegerField(blank=True, null=True)
    blood_pressure_systolic = models.IntegerField(blank=True, null=True)
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamp
    date_recorded = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date_recorded} - {self.weight}kg"
    
    def save(self, *args, **kwargs):
        # Calculate BMI if height and weight are provided
        if self.height and self.weight:
            height_in_meters = self.height / 100
            self.bmi = round(self.weight / (height_in_meters ** 2), 1)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-date_recorded']
        unique_together = ['user', 'date_recorded']
        verbose_name_plural = 'Fitness Progress'


class UserFitnessGoal(models.Model):
    """User's fitness goals - renamed to avoid conflict with CustomUser.fitness_goal"""
    
    GOAL_TYPES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('custom', 'Custom'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fitness_goal_tracking')
    
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    
    # Target metrics
    target_weight = models.FloatField(help_text="Target weight in kg", null=True, blank=True)
    target_body_fat = models.FloatField(help_text="Target body fat percentage", null=True, blank=True)
    target_date = models.DateField(help_text="Date to achieve this goal", null=True, blank=True)
    
    # Weekly targets
    weekly_workout_goal = models.IntegerField(default=3, help_text="Workouts per week")
    weekly_calorie_goal = models.IntegerField(default=2000, help_text="Daily calorie target")
    
    # Status
    is_active = models.BooleanField(default=True)
    achieved = models.BooleanField(default=False)
    achieved_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()}"
    
    def progress_percentage(self):
        """Calculate progress towards weight goal"""
        if not self.target_weight:
            return 0
        
        latest_progress = FitnessProgress.objects.filter(user=self.user).first()
        if not latest_progress:
            return 0
        
        current_weight = latest_progress.weight
        start_weight = FitnessProgress.objects.filter(user=self.user).last()
        start_weight = start_weight.weight if start_weight else current_weight
        
        if self.goal_type == 'weight_loss':
            lost = start_weight - current_weight
            target_loss = start_weight - self.target_weight
            if target_loss > 0:
                return min(100, int((lost / target_loss) * 100))
        elif self.goal_type == 'weight_gain':
            gained = current_weight - start_weight
            target_gain = self.target_weight - start_weight
            if target_gain > 0:
                return min(100, int((gained / target_gain) * 100))
        
        return 0
    
    class Meta:
        verbose_name = 'Fitness Goal'
        verbose_name_plural = 'Fitness Goals'


class WorkoutLog(models.Model):
    """Log individual workouts"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_logs')
    workout_plan = models.ForeignKey('workouts.WorkoutPlan', on_delete=models.SET_NULL, null=True, blank=True)
    
    date = models.DateField(default=timezone.now)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    
    exercises_completed = models.TextField(blank=True, help_text="List of exercises done")
    notes = models.TextField(blank=True)
    felt_difficulty = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.duration_minutes}min"
    
    class Meta:
        ordering = ['-date']