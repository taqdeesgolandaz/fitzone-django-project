from django.db import models
from django.conf import settings
from django.utils import timezone

class WorkoutCategory(models.Model):
    """Workout difficulty categories"""
    
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-dumbbell')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Workout Categories'


class Exercise(models.Model):
    """Individual exercises"""
    
    BODY_PARTS = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulder', 'Shoulder'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('legs', 'Legs'),
        ('cardio', 'Cardio'),
        ('full_body', 'Full Body'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    body_part = models.CharField(max_length=20, choices=BODY_PARTS)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True, related_name='exercises')
    
    # Media
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="YouTube video URL")
    
    # Details
    sets_reps = models.CharField(max_length=50, blank=True, help_text="e.g., 3 sets of 12 reps")
    duration_minutes = models.IntegerField(default=0, help_text="Estimated duration in minutes")
    calories_burn = models.IntegerField(default=0, help_text="Estimated calories burned per session")
    
    # Instructions
    instructions = models.TextField(blank=True)
    tips = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_youtube_embed_url(self):
        """Convert YouTube URL to embed URL"""
        if 'youtu.be' in self.video_url:
            video_id = self.video_url.split('/')[-1]
        elif 'watch?v=' in self.video_url:
            video_id = self.video_url.split('v=')[1].split('&')[0]
        else:
            return self.video_url
        return f"https://www.youtube.com/embed/{video_id}"


class WorkoutPlan(models.Model):
    """Workout plan for users"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
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
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    
    # Exercises in this plan
    exercises = models.ManyToManyField(Exercise, through='WorkoutPlanExercise')
    
    # Duration
    duration_weeks = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    
    # For which membership plan (if restricted)
    required_membership = models.ForeignKey('membership.MembershipPlan', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_difficulty_display()} ({self.get_day_of_week_display()})"
    
    class Meta:
        ordering = ['difficulty', 'day_of_week']


class WorkoutPlanExercise(models.Model):
    """Junction table for workout plan exercises with order"""
    
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    sets = models.IntegerField(default=3)
    reps = models.CharField(max_length=20, default="12")
    rest_seconds = models.IntegerField(default=60)
    
    class Meta:
        ordering = ['order']
        unique_together = ['workout_plan', 'exercise']


class UserWorkoutProgress(models.Model):
    """Track user's workout completion"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_progress')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking
    calories_burned = models.IntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_plan.name} - {self.scheduled_date}"
    
    class Meta:
        unique_together = ['user', 'workout_plan', 'scheduled_date']
        ordering = ['-scheduled_date']