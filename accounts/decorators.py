from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def membership_required(view_func):
    """Decorator to check if user has active membership (admin/staff users are exempt)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Allow admin/staff users to bypass membership requirement
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        if not request.user.membership_active:
            messages.warning(request, '⚠️ You need an active membership to access this feature. Please purchase a membership plan first.')
            return redirect('membership:plans')
        
        return view_func(request, *args, **kwargs)
    return wrapper