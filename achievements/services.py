from django.utils import timezone
from datetime import timedelta
from .models import Badge, UserAchievement, UserProgress
from workouts.models import UserWorkoutProgress
from tracking.models import FitnessProgress
from payments.models import Payment
from trainers.models import TrainerSession

class AchievementService:
    """Service to check and award achievements"""
    
    @staticmethod
    def get_or_create_progress(user):
        """Get or create user progress record"""
        progress, created = UserProgress.objects.get_or_create(user=user)
        return progress
    
    @staticmethod
    def update_workout_stats(user):
        """Update workout-related statistics"""
        progress = AchievementService.get_or_create_progress(user)
        
        # Count total completed workouts
        completed_workouts = UserWorkoutProgress.objects.filter(
            user=user, 
            status='completed'
        )
        progress.total_workouts = completed_workouts.count()
        
        # Calculate streak
        streak = AchievementService.calculate_streak(user)
        progress.current_streak = streak
        if streak > progress.longest_streak:
            progress.longest_streak = streak
        
        # Total calories and minutes
        progress.total_calories = sum(w.calories_burned for w in completed_workouts)
        progress.total_minutes = sum(w.duration_minutes for w in completed_workouts)
        
        progress.save()
        
        # Check for new badges
        AchievementService.check_workout_badges(user, progress)
        AchievementService.check_streak_badges(user, progress)
    
    @staticmethod
    def calculate_streak(user):
        """Calculate current workout streak"""
        completed_workouts = UserWorkoutProgress.objects.filter(
            user=user,
            status='completed'
        ).values_list('scheduled_date', flat=True).distinct()
        
        completed_dates = set(completed_workouts)
        streak = 0
        current_date = timezone.now().date()
        
        while current_date in completed_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    @staticmethod
    def update_weight_stats(user):
        """Update weight-related statistics"""
        progress = AchievementService.get_or_create_progress(user)
        
        weight_records = FitnessProgress.objects.filter(user=user).order_by('date_recorded')
        progress.weight_logged_count = weight_records.count()
        
        if weight_records.count() >= 2:
            first_weight = weight_records.first().weight
            last_weight = weight_records.last().weight
            
            if last_weight < first_weight:
                progress.weight_lost_total = first_weight - last_weight
            else:
                progress.weight_gained_total = last_weight - first_weight
        
        progress.save()
        AchievementService.check_weight_badges(user, progress)
    
    @staticmethod
    def update_membership_stats(user):
        """Update membership-related statistics"""
        progress = AchievementService.get_or_create_progress(user)
        
        from membership.models import UserMembership
        memberships = UserMembership.objects.filter(user=user)
        
        if memberships.exists():
            # Calculate total membership days
            for membership in memberships:
                days = (membership.end_date - membership.start_date).days
                progress.membership_days += days
        
        progress.save()
        AchievementService.check_membership_badges(user, progress)
    
    @staticmethod
    def update_payment_stats(user):
        """Update payment-related statistics"""
        progress = AchievementService.get_or_create_progress(user)
        
        payments = Payment.objects.filter(user=user, status='success')
        progress.total_payments = payments.count()
        progress.total_spent = sum(p.amount for p in payments)
        
        progress.save()
        AchievementService.check_payment_badges(user, progress)
    
    @staticmethod
    def update_trainer_stats(user):
        """Update trainer session statistics"""
        progress = AchievementService.get_or_create_progress(user)
        
        sessions = TrainerSession.objects.filter(user=user, status='completed')
        progress.trainer_sessions = sessions.count()
        
        progress.save()
        AchievementService.check_trainer_badges(user, progress)
    
    @staticmethod
    def check_workout_badges(user, progress):
        """Check and award workout badges"""
        badge_requirements = [
            ('First Step', 1),
            ('Getting Started', 10),
            ('Fitness Enthusiast', 50),
            ('Workout Warrior', 100),
            ('Fitness Legend', 500),
        ]
        
        for badge_name, requirement in badge_requirements:
            if progress.total_workouts >= requirement:
                AchievementService.award_badge(user, badge_name)
    
    @staticmethod
    def check_streak_badges(user, progress):
        """Check and award streak badges"""
        badge_requirements = [
            ('Consistency King', 7),
            ('Unstoppable', 30),
            ('Beast Mode', 100),
        ]
        
        for badge_name, requirement in badge_requirements:
            if progress.current_streak >= requirement:
                AchievementService.award_badge(user, badge_name)
    
    @staticmethod
    def check_weight_badges(user, progress):
        """Check and award weight badges"""
        if progress.weight_logged_count >= 10:
            AchievementService.award_badge(user, 'Weight Watcher')
        
        if progress.weight_lost_total >= 5:
            AchievementService.award_badge(user, 'Weight Loss Champion')
        
        if progress.weight_lost_total >= 15:
            AchievementService.award_badge(user, 'Transformation Master')
    
    @staticmethod
    def check_membership_badges(user, progress):
        """Check and award membership badges"""
        if progress.total_payments >= 1:
            AchievementService.award_badge(user, 'New Member')
        
        if progress.membership_days >= 90:
            AchievementService.award_badge(user, 'Loyal Member')
        
        if progress.membership_days >= 365:
            AchievementService.award_badge(user, 'VIP Member')
    
    @staticmethod
    def check_payment_badges(user, progress):
        """Check and award payment badges"""
        if float(progress.total_spent) >= 10000:
            AchievementService.award_badge(user, 'Century Club')
    
    @staticmethod
    def check_trainer_badges(user, progress):
        """Check and award trainer badges"""
        if progress.trainer_sessions >= 1:
            AchievementService.award_badge(user, 'Seeker of Knowledge')
        
        if progress.trainer_sessions >= 10:
            AchievementService.award_badge(user, 'Dedicated Learner')
    
    @staticmethod
    def award_badge(user, badge_name):
        """Award a badge to user"""
        try:
            badge = Badge.objects.get(name=badge_name, is_active=True)
            achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                badge=badge
            )
            
            if created:
                # Update points
                progress = AchievementService.get_or_create_progress(user)
                progress.total_points += badge.points
                progress.save()
                
                # Create notification
                from notifications.services import NotificationService
                NotificationService.create_notification(
                    user=user,
                    title=f"🏆 New Achievement Unlocked!",
                    message=f"You've earned the '{badge.name}' badge! +{badge.points} points",
                    notification_type='achievement',
                    link='/achievements/'
                )
                return True
        except Badge.DoesNotExist:
            pass
        return False
    
    @staticmethod
    def get_user_badges(user):
        """Get all badges earned by user"""
        return UserAchievement.objects.filter(user=user).select_related('badge')
    
    @staticmethod
    def get_available_badges(user):
        """Get badges user hasn't earned yet"""
        earned_badge_ids = UserAchievement.objects.filter(user=user).values_list('badge_id', flat=True)
        return Badge.objects.filter(is_active=True).exclude(id__in=earned_badge_ids)