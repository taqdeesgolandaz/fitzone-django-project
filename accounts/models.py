from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class CustomUser(AbstractUser):
    """Custom User Model for FitZone"""

    current_session_key = models.CharField(max_length=100, blank=True, null=True)
    
    # Preferred language for the user (used for UI localization)
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
    ]
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    
    # Personal Information
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
        null=True
    )
    height = models.FloatField(help_text="Height in cm", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    
    # Fitness Goals
    FITNESS_GOALS = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('general_fitness', 'General Fitness'),
    ]
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOALS, blank=True, null=True)
    
    # Profile Picture
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Membership tracking
    membership_expiry = models.DateTimeField(null=True, blank=True)
    membership_active = models.BooleanField(default=False)
    
    # For JWT and groups compatibility
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_groups',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions',
        related_query_name='custom_user',
    )
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"
    
    def get_full_name(self):
        """Return full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.full_name:
            return self.full_name
        return self.username
    
    def calculate_bmi(self):
        """Calculate BMI for the user"""
        if self.height and self.weight:
            height_in_meters = self.height / 100
            bmi = self.weight / (height_in_meters ** 2)
            return round(bmi, 1)
        return None
    
    def get_bmi_category(self):
        """Get BMI category"""
        bmi = self.calculate_bmi()
        if bmi:
            if bmi < 18.5:
                return "Underweight"
            elif 18.5 <= bmi < 25:
                return "Normal"
            elif 25 <= bmi < 30:
                return "Overweight"
            else:
                return "Obese"
        return "Not available"
    
    def has_active_membership(self):
        """Check if membership is active"""
        if self.membership_active and self.membership_expiry:
            return timezone.now() <= self.membership_expiry
        return False
    
def save(self, *args, **kwargs):
    # Auto-generate full_name from first_name and last_name
    if self.first_name and self.last_name:
        self.full_name = f"{self.first_name} {self.last_name}"
    elif self.first_name:
        self.full_name = self.first_name
    
    # Optimize profile picture
    if self.profile_picture:
        self.optimize_profile_picture()
    
    super().save(*args, **kwargs)

def optimize_profile_picture(self):
    """Optimize and resize profile picture to fit perfectly"""
    try:
        img = Image.open(self.profile_picture.path)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (26, 26, 46))  # FitZone dark background
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Calculate new size (300x300 square)
        target_size = (300, 300)
        
        # Crop to square first
        min_dimension = min(img.size)
        left = (img.size[0] - min_dimension) / 2
        top = (img.size[1] - min_dimension) / 2
        right = (img.size[0] + min_dimension) / 2
        bottom = (img.size[1] + min_dimension) / 2
        img = img.crop((left, top, right, bottom))
        
        # Resize to target size
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Update the file
        self.profile_picture.save(
            self.profile_picture.name,
            ContentFile(output.read()),
            save=False
        )
    except Exception as e:
        print(f"Error optimizing profile picture: {e}")
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'