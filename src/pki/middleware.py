from django.conf import settings
from django.core.exceptions import PermissionDenied



class ClientCertMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'ECS_REQUIRE_CLIENT_CERTS', False):
            return self.get_response(request)

        if request.user.is_authenticated:
            profile = request.user.profile
            if (profile.is_internal or profile.is_omniscient_member) and \
                    request.META.get('HTTP_X_SSL_CLIENT_VERIFY') != 'SUCCESS':
                raise PermissionDenied()

        response = self.get_response(request)
        return response