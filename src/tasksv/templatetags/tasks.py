from django.template import Library

from src.tasksv.models import TaskType


register = Library()


@register.filter
def task_type_name(slug):
    return TaskType.objects.filter(workflow_node__uid=slug).order_by('-pk')[0].trans_name
