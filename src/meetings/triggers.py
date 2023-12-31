from django.dispatch import receiver

from src.meetings import signals
from src.meetings.cache import flush_meeting_page_cache
from src.meetings.models import Participation
from src.votes.models import Vote
from src.workflow.signals import token_marked_deleted


def _flush_cache(meeting):
    from meetings.views import submission_list

    flush_meeting_page_cache(meeting, submission_list)


@receiver(signals.on_meeting_start)
def on_meeting_start(sender, **kwargs):
    meeting = kwargs["meeting"]
    _flush_cache(meeting)


@receiver(signals.on_meeting_end)
def on_meeting_end(sender, **kwargs):
    meeting = kwargs["meeting"]

    for vote in Vote.objects.filter(top__meeting=meeting):
        vote.save()  # trigger post_save for all votes

    for top in meeting.additional_entries.exclude(
        pk__in=Vote.objects.exclude(top=None).values("top__pk").query
    ):
        # update eventual existing vote from vote preperation
        vote, created = Vote.objects.update_or_create(
            submission_form=top.submission.current_submission_form,
            defaults={"top": top, "result": "3a", "is_draft": False},
        )
        top.is_open = False
        top.save()

    _flush_cache(meeting)


@receiver(signals.on_meeting_date_changed)
def on_meeting_date_changed(sender, **kwargs):
    meeting = kwargs["meeting"]
    _flush_cache(meeting)


@receiver(signals.on_meeting_top_jump)
def on_meeting_top_jump(sender, **kwargs):
    meeting = kwargs["meeting"]
    timetable_entry = kwargs["timetable_entry"]
    _flush_cache(meeting)


@receiver(signals.on_meeting_top_add)
def on_meeting_top_add(sender, **kwargs):
    meeting = kwargs["meeting"]
    timetable_entry = kwargs["timetable_entry"]
    _flush_cache(meeting)


@receiver(signals.on_meeting_top_delete)
def on_meeting_top_delete(sender, **kwargs):
    meeting = kwargs["meeting"]
    timetable_entry = kwargs["timetable_entry"]
    _flush_cache(meeting)


@receiver(signals.on_meeting_top_index_change)
def on_meeting_top_index_change(sender, **kwargs):
    meeting = kwargs["meeting"]
    timetable_entry = kwargs["timetable_entry"]
    _flush_cache(meeting)


@receiver(token_marked_deleted)
def workflow_token_marked_deleted(sender, **kwargs):
    if sender.task:
        Participation.objects.filter(
            entry__meeting__started=None, task=sender.task
        ).delete()
