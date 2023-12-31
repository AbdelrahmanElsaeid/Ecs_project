from django import template

from src.tasksv.models import Task
from src.users.utils import sudo
from src.core.diff import diff_submission_forms
from src.core.models import SubmissionForm

register = template.Library()

@register.filter
def amendment_reviewer(notification):
    with sudo():
        closed_tasks = Task.objects.for_data(notification.amendmentnotification).closed()
        try:
            task = closed_tasks.filter(
                task_type__workflow_node__uid='executive_amendment_review'
            ).order_by('-created_at')[0]
            return task.assigned_to
        except IndexError:
            pass

@register.filter
def diff_from_docstash(docstash):
    extra = docstash['extra']
    old_submission_form = SubmissionForm.objects.get(id=extra['old_submission_form_id'])
    new_submission_form = SubmissionForm.objects.get(id=extra['new_submission_form_id'])
    return diff_submission_forms(old_submission_form, new_submission_form).html()

@register.filter
def diff(notification, plainhtml=False):
    return notification.get_diff(plainhtml=plainhtml)
