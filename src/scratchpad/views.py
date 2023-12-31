from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404

from src.scratchpad.forms import ScratchPadForm
from src.scratchpad.models import ScratchPad
from src.core.models.submissions import Submission




def popup(request, scratchpad_pk=None):
    submission = None
    submission_pk = request.GET.get('submission')
    if submission_pk:
        submission = get_object_or_404(Submission, pk=submission_pk)

    if scratchpad_pk:
        scratchpad = get_object_or_404(ScratchPad, owner=request.user,
            pk=scratchpad_pk)
        submission = scratchpad.submission
    else:
        scratchpad, created = ScratchPad.objects.get_or_create(
            owner=request.user, submission=submission)

    form = ScratchPadForm(request.POST or None, instance=scratchpad,
        prefix='scratchpad')
    if request.method == 'POST' and form.is_valid():
        form.save()

    return render(request, 'scratchpad/scratchpad.html', {
        'form': form,
        'scratchpad': scratchpad,
        'submission': submission,
    })


def popup_list(request):
    scratchpads = (ScratchPad.objects
        .filter(owner=request.user, text__isnull=False)
        .exclude(text='')
        .order_by('-modified_at')[:100]
    )
    return render(request, 'scratchpad/list.html', {
        'scratchpads': scratchpads,
    })