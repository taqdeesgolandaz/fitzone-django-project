from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime

class Trainer(models.Model):
    """Trainer profile model"""
    
    SPECIALIZATIONS = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('cardio', 'Cardio'),
        ('strength_training', 'Strength Training'),
        ('yoga', 'Yoga'),
        ('nutrition', 'Nutrition'),
        ('general_fitness', 'General Fitness'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner (1-2 years)'),
        ('intermediate', 'Intermediate (3-5 years)'),
        ('advanced', 'Advanced (5-8 years)'),
        ('expert', 'Expert (8+ years)'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainer_profile')
    
    # Personal Info
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='trainers/', blank=True, null=True)
    
    # Professional Info
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    years_of_experience = models.IntegerField(default=0)
    bio = models.TextField()
    qualifications = models.TextField(help_text="List qualifications, certifications")
    achievements = models.TextField(blank=True)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=500, help_text="Per hour rate (if applicable)")
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1999, help_text="Monthly subscription rate")
    
    # Availability (JSON)
    availability = models.JSONField(default=dict, help_text="Weekly availability schedule")
    
    # Status
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    # Position for manual ordering in admin (lower = higher on list)
    position = models.PositiveIntegerField(default=0, db_index=True)
    
    # Ratings
    total_ratings = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Timestamps
    joined_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.get_specialization_display()}"

    def save(self, *args, **kwargs):
        # Ensure new trainers are appended to the end if position not set
        if self.pk is None and (self.position is None or self.position == 0):
            max_pos = Trainer.objects.aggregate(models.Max('position'))['position__max']
            self.position = (max_pos or 0) + 1
        super().save(*args, **kwargs)
    
    def get_rating_stars(self):
        """Return star rating as HTML"""
        full_stars = int(self.average_rating)
        half_star = 1 if self.average_rating - full_stars >= 0.5 else 0
        return {'full': full_stars, 'half': half_star, 'empty': 5 - full_stars - half_star}
    
    class Meta:
        ordering = ['position', '-is_featured', '-average_rating']


class TrainerSession(models.Model):
    """Booking sessions with trainers"""
    
    SESSION_TYPES = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='booked_sessions')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='sessions')
    
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='online')
    session_date = models.DateField()
    session_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    
    # Pricing (monthly subscription)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly subscription amount")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional Info
    user_notes = models.TextField(blank=True, help_text="Any specific goals or concerns")
    trainer_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Meeting Link (for online sessions)
    meeting_link = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.trainer.full_name} - {self.session_date}"
    
    def is_upcoming(self):
        """Check if session is in the future"""
        from django.utils import timezone
        import datetime
        
        # Combine date and time to make datetime
        session_datetime = datetime.datetime.combine(self.session_date, self.session_time)
        # Make it timezone aware
        session_datetime = timezone.make_aware(session_datetime)
        return session_datetime > timezone.now()
    
    def can_cancel(self):
        """Check if session can be cancelled"""
        return self.status == 'pending' and self.is_upcoming()
    
    def get_formatted_amount(self):
        """Return formatted amount with ₹ symbol"""
        return f"₹{self.amount}"
    
    class Meta:
        ordering = ['-session_date', '-session_time']


class TrainerReview(models.Model):
    """Reviews for trainers"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='reviews')
    session = models.ForeignKey(TrainerSession, on_delete=models.CASCADE, null=True, blank=True)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.trainer.full_name} - {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']