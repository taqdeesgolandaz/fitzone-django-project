from django.db import models
from django.conf import settings
from django.utils import timezone

class Badge(models.Model):
    """Achievement badges users can earn"""
    
    BADGE_TYPES = [
        ('workout', 'Workout Badge'),
        ('streak', 'Streak Badge'),
        ('weight', 'Weight Goal Badge'),
        ('membership', 'Membership Badge'),
        ('social', 'Social Badge'),
        ('special', 'Special Badge'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='bronze')
    
    # Icon (Font Awesome class)
    icon = models.CharField(max_length=50, default='fas fa-medal')
    
    # Requirement
    requirement_value = models.IntegerField(help_text="Number of actions required to earn this badge")
    requirement_unit = models.CharField(max_length=50, blank=True, help_text="e.g., workouts, days, kg")
    
    # Points awarded
    points = models.IntegerField(default=10)
    
    # Image
    image = models.ImageField(upload_to='badges/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"
    
    def get_color(self):
        """Get color for badge based on difficulty"""
        colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0',
            'gold': '#FFD700',
            'platinum': '#E5E4E2',
            'diamond': '#B9F2FF',
        }
        return colors.get(self.difficulty, '#E94560')
    
    class Meta:
        ordering = ['difficulty', 'requirement_value']


class UserAchievement(models.Model):
    """Track user's earned achievements"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    
    earned_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']


class UserProgress(models.Model):
    """Track user's progress towards achievements"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_stats')
    
    # Workout stats
    total_workouts = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_calories = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)
    
    # Weight stats
    weight_logged_count = models.IntegerField(default=0)
    weight_lost_total = models.FloatField(default=0)
    weight_gained_total = models.FloatField(default=0)
    
    # Membership stats
    membership_days = models.IntegerField(default=0)
    total_payments = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Session stats
    trainer_sessions = models.IntegerField(default=0)
    
    # Points
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level} - {self.total_points} pts"
    
    def calculate_level(self):
        """Calculate user level based on points"""
        if self.total_points < 100:
            return 1
        elif self.total_points < 250:
            return 2
        elif self.total_points < 500:
            return 3
        elif self.total_points < 1000:
            return 4
        elif self.total_points < 2000:
            return 5
        else:
            return 5 + (self.total_points // 1000)
    
    def save(self, *args, **kwargs):
        self.level = self.calculate_level()
        super().save(*args, **kwargs)