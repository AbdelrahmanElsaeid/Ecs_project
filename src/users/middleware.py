


from django.contrib.auth.models import AnonymousUser
from src.users.user_context import current_user_store

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if not hasattr(user, 'is_authenticated'):
            user = AnonymousUser()

        # Store the current user in threading.local()
        current_user_store.current_user = user

        response = self.get_response(request)

        # Optionally, you can perform additional logic after the view is called.

        return response
