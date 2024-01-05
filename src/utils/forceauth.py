"""
Middleware that forces Authentication.
"""
# from django.shortcuts import redirect
# from django.conf import settings


# def exempt(view):
#     view._forceauth_exempt = True
#     return view
# class ForceAuth:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         return response

#     def process_view(self, request, view, args, kwargs):
#         if not getattr(view, '_forceauth_exempt') and request.user.is_anonymous():
#             return redirect(settings.LOGIN_URL + '?next=%s' % request.path)



from django.shortcuts import redirect
from django.conf import settings

def exempt(view):
    view._forceauth_exempt = True
    return view

class ForceAuth:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     # Check if the view is a class-based view
    #     if hasattr(view_func, 'as_view'):
    #         view_class = view_func
    #     else:
    #         # For function-based views, try to get the original view class
    #         try:
    #             view_class = view_func.view_class
    #         except AttributeError:
    #             # If it fails, assume it's a regular function-based view
    #             view_class = None

    #     # Check if the view or view class is exempt from forceauth
    #     force_auth_exempt = getattr(view_class, '_forceauth_exempt', False) if view_class else False
    #     if not force_auth_exempt and request.user.is_anonymous():
    #         return redirect(f"{settings.LOGIN_URL}?next={request.path}")
    #     return None
    def process_view(self, request, view, args, kwargs):
        if not getattr(view, '_forceauth_exempt') and request.user.is_anonymous():
            return redirect(settings.LOGIN_URL + '?next=%s' % request.path)

