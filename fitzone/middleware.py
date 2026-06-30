import sys
from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin


def _is_local_dev_host(host: str) -> bool:
    host = (host or '').split(':')[0].lower()
    if not host:
        return False
    return host in {'localhost', '127.0.0.1', '0.0.0.0', '::1'} or host.startswith(('10.', '192.168.', '172.'))


class LocalDevCSRFExemptMiddleware(MiddlewareMixin):
    """Allow login POSTs from local network hosts to work reliably in development."""

    def process_request(self, request):
        if request.method != 'POST':
            return

        local_login_paths = {'/login/', '/accounts/login/'}
        if request.path in local_login_paths and _is_local_dev_host(request.get_host()):
            request._dont_enforce_csrf_checks = True


class LocalCSRFCookieMiddleware(MiddlewareMixin):
    """Ensure a CSRF cookie is set in local development environments. (DISABLED)"""
    pass


class SessionDebugMiddleware(MiddlewareMixin):
    """Log session state for every request during local development. (DISABLED)"""
    pass
