from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.translation import gettext as _

from src.tags.models import Tag
from src.tags.forms import TagForm, TagAssignForm
from src.users.utils import user_flag_required
from src.core.models import Submission


@user_flag_required('is_internal')
def index(request):
    return render(request, 'tags/index.html', {
        'tags': Tag.objects.all(),
    })


@user_flag_required('is_internal')
def edit(request, pk=None):
    instance = None
    if pk is not None:
        instance = get_object_or_404(Tag, pk=pk)
    form = TagForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('tags:index')
    return render(request, 'tags/edit.html', {
        'form': form,
    })


@user_flag_required('is_internal')
def assign(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = TagAssignForm(request.POST or None, prefix='assign_tags')
    form.fields['tags'].initial = submission.tags.all()
    if request.method == 'POST' and form.is_valid():
        submission.tags = form.cleaned_data['tags']
        return redirect('tags:assign', submission_pk=submission_pk)
    return render(request, 'tags/assign.html', {
        'submission': submission,
        'form': form,
    })


@user_flag_required('is_internal')
def delete(request, pk=None):
    tag = get_object_or_404(Tag, pk=pk)
    if tag.submissions.exists():
        messages.error(request,
            _('This tag is still used and can\'t be deleted.'))
        return redirect('tags:edit', pk=pk)
    tag.delete()
    return redirect('tags:index')