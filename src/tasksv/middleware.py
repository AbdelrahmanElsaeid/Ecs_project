from django.conf import settings

from src.tasksv.models import Task
from src.utils.lazy import LazyList



class RelatedTasksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _get_related_tasks(self, request):
        user_tasks = Task.objects.for_user(request.user).filter(closed_at=None).select_related('task_type')
        assigned_tasks = user_tasks.filter(assigned_to=request.user, deleted_at=None)
        for t in assigned_tasks:
            if request.path in t.get_final_urls():
                yield t

    def __call__(self, request):
        if not request.user.is_authenticated or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        request.related_tasks = LazyList(self._get_related_tasks, request)
        return self.get_response(request)
