

import threading

current_user_store = threading.local()

class GlobalUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user:
            current_user_store.user = request.user

        response = self.get_response(request)

        if hasattr(current_user_store, 'user'):
            del current_user_store.user

        return response
  