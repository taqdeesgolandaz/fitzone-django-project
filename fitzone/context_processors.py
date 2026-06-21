from django.contrib import messages

def clear_messages_on_get(request):
    """Clear messages on GET requests to prevent stale messages"""
    if request.method == 'GET':
        storage = messages.get_messages(request)
        storage.used = True
    return {}