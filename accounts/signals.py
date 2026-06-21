from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver


def ensure_single_session(request, user):
    """Make sure only one active session exists for this user."""
    if not request.session.session_key:
        request.session.save()

    current_session_key = request.session.session_key
    if user.current_session_key and user.current_session_key != current_session_key:
        try:
            old_session = Session.objects.get(session_key=user.current_session_key)
            old_session.delete()
        except Session.DoesNotExist:
            pass

    user.current_session_key = current_session_key
    user.save(update_fields=['current_session_key'])


@receiver(user_logged_in)
def restrict_single_session(sender, request, user, **kwargs):
    """Logout user from other devices"""
    ensure_single_session(request, user)
