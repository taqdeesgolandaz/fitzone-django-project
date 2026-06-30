from django.shortcuts import redirect, render
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
        
        if not getattr(request.user, 'has_active_membership', lambda: False)():
            # Render a dedicated membership required template instead of flashing a message
            return render(request, 'tracking/membership_required.html')
        
        return view_func(request, *args, **kwargs)
    return wrapper