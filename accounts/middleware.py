from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.session_key:
                request.session.save()

            current_session_key = request.session.session_key

            # Check if user's saved session key matches current session
            if request.user.current_session_key and request.user.current_session_key != current_session_key:
                logout(request)
                messages.warning(request, 'You have been logged out because you logged in from another device.')
                return redirect('login')

        response = self.get_response(request)
        return response    