from django.db import models
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlparse, parse_qs

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
    
    VIDEO_FALLBACKS = {
        'bench press': ['https://www.youtube.com/watch?v=SCVCLChPQFY'],
        'deadlift': ['https://www.youtube.com/watch?v=X1TuhAn6C-g'],
        'deadlifts': ['https://www.youtube.com/watch?v=X1TuhAn6C-g'],
        'barbell squat': ['https://www.youtube.com/watch?v=aclHkVaku9U'],
        'push ups': ['https://www.youtube.com/watch?v=IODxDxX7oi4'],
        'push-ups': ['https://www.youtube.com/watch?v=IODxDxX7oi4'],
        'plank': ['https://www.youtube.com/watch?v=ASdvN_XEl_c'],
        'pull ups': ['https://www.youtube.com/watch?v=b2MRk2eV96M'],
        'pull-ups': ['https://www.youtube.com/watch?v=b2MRk2eV96M'],
        'dips': ['https://www.youtube.com/watch?v=2z8lSnHhBvE'],
        'lunges': ['https://www.youtube.com/watch?v=wrwwXE_x-pQ'],
        'walking lunges': ['https://www.youtube.com/watch?v=wrwwXE_x-pQ'],
        'handstand pushups': ['https://www.youtube.com/watch?v=zA2nuzsSDKQ'],
        'muscle ups': ['https://www.youtube.com/watch?v=_eQ2gw_Gg5Y'],
        'romanian deadlift': ['https://www.youtube.com/watch?v=ybK7H-WsPAS'],
        'leg press': ['https://www.youtube.com/watch?v=IZxyjW7MPJQ'],
        'jump squats': ['https://www.youtube.com/watch?v=Ow0PDAcrJW0'],
        'pistol squat': ['https://www.youtube.com/watch?v=sZfNXl8uDFs'],
        'pistol squats': ['https://www.youtube.com/watch?v=sZfNXl8uDFs'],
        'mountain climbers': ['https://www.youtube.com/watch?v=boa8XbnkLlc'],
        'jumping jacks': ['https://www.youtube.com/watch?v=dmYwZH_BNd0'],
        'burpees': ['https://www.youtube.com/watch?v=1YMLT8MYJ9w'],
        'bench press': ['https://www.youtube.com/watch?v=SCVCLChPQFY'],
        'overhead press': ['https://www.youtube.com/watch?v=qEwKCR5JCog'],
        'dumbbell curl': ['https://www.youtube.com/watch?v=sAq_ocpRh_I'],
        'tricep pushdown': ['https://www.youtube.com/watch?v=2-LAMcpzODU'],
        'leg curl': ['https://www.youtube.com/watch?v=1Tq3QdILLpc'],
        'leg extension': ['https://www.youtube.com/watch?v=AmCqjGRS6m0'],
        'calf raise': ['https://www.youtube.com/watch?v=BT1n6c80Z3E'],
        'hamstring stretch': ['https://www.youtube.com/watch?v=5T5-BRw_3qk'],
        'shoulder stretch': ['https://www.youtube.com/watch?v=H3L61lh8GYk'],
        'hip flexor stretch': ['https://www.youtube.com/watch?v=VnAqD_mJ4Lk'],
    }

    @staticmethod
    def _normalize_exercise_name(name):
        if not name:
            return ''
        return ''.join(ch for ch in name.lower() if ch.isalnum() or ch.isspace()).strip()

    @staticmethod
    def _youtube_embed_url(video_url):
        if not video_url:
            return ''

        parsed = urlparse(video_url)
        hostname = parsed.hostname or ''
        path = parsed.path or ''
        query = parse_qs(parsed.query)

        video_id = ''
        if 'youtu.be' in hostname:
            video_id = path.lstrip('/')
        elif 'youtube.com' in hostname:
            if path.startswith('/watch'):
                video_id = query.get('v', [''])[0]
            elif path.startswith('/embed/'):
                video_id = path.split('/embed/')[1]
            elif path.startswith('/shorts/'):
                video_id = path.split('/shorts/')[1]

        if not video_id:
            return video_url

        return f"https://www.youtube.com/embed/{video_id}"

    def get_youtube_embed_urls(self):
        urls = []
        if self.video_url:
            primary_url = self._youtube_embed_url(self.video_url)
            if primary_url:
                urls.append(primary_url)

        normalized_name = self._normalize_exercise_name(self.name)
        fallback_urls = self.VIDEO_FALLBACKS.get(normalized_name, [])
        for fallback_url in fallback_urls:
            embed_url = self._youtube_embed_url(fallback_url)
            if embed_url and embed_url not in urls:
                urls.append(embed_url)

        return urls

    def get_youtube_embed_url(self):
        urls = self.get_youtube_embed_urls()
        return urls[0] if urls else ''


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