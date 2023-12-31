from django.urls import reverse
from django.utils.translation import gettext as _
from django.dispatch import receiver

from src.workflow import Activity, guard, register
from src.workflow.patterns import Generic
from src.meetings.signals import on_meeting_start, on_meeting_end
from src.notifications.models import (
    Notification, CompletionReportNotification, ProgressReportNotification,
    SafetyNotification, CenterCloseNotification, AmendmentNotification,
    NOTIFICATION_MODELS,
)


for cls in NOTIFICATION_MODELS:
    register(cls, autostart_if=lambda n, created: n.submission_forms.exists() and not n.workflow.workflows.exists())


@guard(model=Notification)
def is_susar(wf):
    return SafetyNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_report(wf):
    return CompletionReportNotification.objects.filter(pk=wf.data.pk).exists() or ProgressReportNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_center_close(wf):
    return CenterCloseNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def is_amendment(wf):
    return AmendmentNotification.objects.filter(pk=wf.data.pk).exists()

@guard(model=Notification)
def needs_further_review(wf):
    return not wf.data.answer.is_valid

@guard(model=Notification)
def is_rejected_and_final(wf):
    return (wf.data.answer.is_rejected and wf.data.answer.is_final_version)

@guard(model=Notification)
def is_substantial(wf):
    return wf.data.amendmentnotification.is_substantial

@guard(model=Notification)
def needs_signature(wf):
    amendment = wf.data.amendmentnotification
    return amendment.needs_signature and not amendment.is_substantial

@guard(model=Notification)
def needs_distribution(wf):
    amendment = wf.data.amendmentnotification
    return not amendment.is_substantial and not amendment.needs_signature

class BaseNotificationReview(Activity):
    def get_url(self):
        return reverse('notifications:edit_notification_answer',
            kwargs={'notification_pk': self.workflow.data.pk})

    def receive_token(self, source, trail=(), repeated=False):
        token = super().receive_token(source, trail=trail, repeated=repeated)
        if trail:
            prev = trail[0]
            if prev.node.uid == 'start':
                prev = prev.trail.first()
            elif prev.node.uid == 'wait_for_meeting':
                prev = prev.trail.first().trail.first()
            if prev:
                token.task.review_for = prev.task
                token.task.save()
        return token

class InitialAmendmentReview(BaseNotificationReview):
    class Meta:
        model = Notification
        
    def get_choices(self):
        return (
            (True, _('Acknowledge'), 'success'),
            (False, _('Reject'), 'danger'),
        )

    def pre_perform(self, choice):
        if not choice:
            answer = self.workflow.data.answer
            answer.is_valid = True
            answer.is_rejected = True
            answer.is_final_version = True
            answer.save()


class EditNotificationAnswer(BaseNotificationReview):
    class Meta:
        model = Notification

    def is_repeatable(self):
        return True
    
    def get_choices(self):
        return (
            (True, _('Ready'), 'success'),
            (False, _('Needs further review'), 'info'),
        )
    
    def pre_perform(self, choice):
        answer = self.workflow.data.answer
        answer.is_valid = choice
        answer.save()


class SimpleNotificationReview(BaseNotificationReview):
    class Meta:
        model = Notification

    def get_choices(self):
        return (
            (True, _('Ready'), 'success'),
            (False, _('Reject'), 'danger'),
        )

    def pre_perform(self, choice):
        if not choice:
            answer = self.workflow.data.answer
            answer.is_valid = True
            answer.is_rejected = True
            answer.is_final_version = True
            answer.save()


class WaitForMeeting(Generic):
    class Meta:
        model = Notification

    def receive_token(self, source, trail=()):
        notification = self.workflow.data
        notification.amendmentnotification.schedule_to_meeting()
        return super().receive_token(source, trail=trail)

    def is_locked(self):
        return not self.workflow.data.amendmentnotification.meeting.ended

    @staticmethod
    @receiver(on_meeting_start)
    def on_meeting_start(sender, **kwargs):
        meeting = kwargs['meeting']
        for amendment in meeting.amendments.all():
            amendment.answer.is_valid = False
            amendment.answer.save()

    @staticmethod
    @receiver(on_meeting_end)
    def on_meeting_end(sender, **kwargs):
        meeting = kwargs['meeting']
        for amendment in meeting.amendments.all():
            amendment.workflow.unlock(WaitForMeeting)
        meeting.amendments.filter(answer__is_valid=False).update(meeting=None)


class SignNotificationAnswer(Activity):
    class Meta:
        model = Notification

    def get_choices(self):
        return (
            (True, 'ok', 'success'),
            (False, 'pushback', 'warning'),
        )

    def get_url(self):
        return reverse('notifications:notification_answer_sign', kwargs={'notification_pk': self.workflow.data.pk})

    def pre_perform(self, choice):
        answer = self.workflow.data.answer
        if choice:
            answer.distribute()

class AutoDistributeNotificationAnswer(Generic):
    class Meta:
        model = Notification

    def handle_token(self, token):
        answer = self.workflow.data.answer
        answer.distribute()

        # XXX: need to render PDF after distribute, to have new vote extension date already set
        answer.render_pdf_document()
        super().handle_token(token)
