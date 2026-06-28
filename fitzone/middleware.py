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
            print(f"[LocalDevCSRFExemptMiddleware] bypassing CSRF for local login POST to {request.path}", file=sys.stderr)


class LocalCSRFCookieMiddleware(MiddlewareMixin):
    """Ensure a CSRF cookie is set in local development environments."""

    def process_request(self, request):
        if not settings.DEBUG:
            return

        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')
        if csrf_cookie_name in request.COOKIES:
            return

        if request.method == 'POST':
            token = (
                request.POST.get('csrfmiddlewaretoken') or
                request.POST.get(csrf_cookie_name) or
                request.META.get('HTTP_X_CSRFTOKEN')
            )
            print(f"[LocalCSRFCookieMiddleware] POST tokens csrfmiddlewaretoken={request.POST.get('csrfmiddlewaretoken')} x-csrftoken={request.META.get('HTTP_X_CSRFTOKEN')} cookie={request.COOKIES.get(csrf_cookie_name)}", file=sys.stderr)
            if token:
                request.COOKIES[csrf_cookie_name] = token
                print(f"[LocalCSRFCookieMiddleware] injected csrftoken from POST into request.COOKIES", file=sys.stderr)

    def process_response(self, request, response):
        if not settings.DEBUG:
            return response

        csrf_cookie_name = getattr(settings, 'CSRF_COOKIE_NAME', 'csrftoken')
        if csrf_cookie_name in request.COOKIES:
            return response

        # Only set the cookie on safe requests so we don't interfere with POST flows.
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return response

        token = get_token(request)
        response.set_cookie(
            csrf_cookie_name,
            token,
            secure=getattr(settings, 'CSRF_COOKIE_SECURE', False),
            httponly=getattr(settings, 'CSRF_COOKIE_HTTPONLY', False),
            samesite=getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Lax'),
            path=getattr(settings, 'CSRF_COOKIE_PATH', '/'),
            domain=getattr(settings, 'CSRF_COOKIE_DOMAIN', None),
        )
        print(f"[LocalCSRFCookieMiddleware] set csrf cookie on response for {request.path}", file=sys.stderr)
        return response


class SessionDebugMiddleware(MiddlewareMixin):
    """Log session state for every request during local development."""

    def __call__(self, request):
        response = self.get_response(request)

        if settings.DEBUG:
            if request.user.is_authenticated:
                print(
                    f"[SESSION] Authenticated user={request.user.username} "
                    f"session_key={request.session.session_key} "
                    f"cookie={request.COOKIES.get(settings.SESSION_COOKIE_NAME)}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"[SESSION] Not authenticated cookie={request.COOKIES.get(settings.SESSION_COOKIE_NAME)}",
                    file=sys.stderr,
                )
        return response
