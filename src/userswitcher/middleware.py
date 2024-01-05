from django.contrib.auth.models import User
from src.userswitcher import SESSION_KEY



class UserSwitcherMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if SESSION_KEY in request.session:
            try:
                request.original_user = request.user
                request.user = User.objects.get(pk=request.session[SESSION_KEY])
            except User.DoesNotExist:
                pass

        response = self.get_response(request)

        if hasattr(request, 'original_user'):
            request.user = request.original_user
            del request.original_user

        return response
