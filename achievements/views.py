from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .services import AchievementService
from .models import UserProgress, Badge

@login_required
def achievements_dashboard(request):
    """User achievements dashboard"""
    user = request.user
    
    # Get earned badges
    earned_badges = AchievementService.get_user_badges(user)
    
    # Get available badges to earn
    available_badges = AchievementService.get_available_badges(user)
    
    # Get user progress stats
    progress, created = UserProgress.objects.get_or_create(user=user)
    
    # Group badges by difficulty
    badge_groups = {
        'bronze': [],
        'silver': [],
        'gold': [],
        'platinum': [],
        'diamond': [],
    }
    
    for achievement in earned_badges:
        badge_groups[achievement.badge.difficulty].append(achievement)
    
    context = {
        'earned_badges': earned_badges,
        'available_badges': available_badges[:12],  # Show top 12 available
        'progress': progress,
        'badge_groups': badge_groups,
        'total_earned': earned_badges.count(),
        'total_available': Badge.objects.filter(is_active=True).count(),
    }
    return render(request, 'achievements/dashboard.html', context)


@login_required
def badge_detail(request, badge_id):
    """View badge details"""
    badge = get_object_or_404(Badge, id=badge_id)
    return render(request, 'achievements/badge_detail.html', {'badge': badge})