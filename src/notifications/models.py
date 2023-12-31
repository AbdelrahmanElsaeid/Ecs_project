from django.db import models

# Create your models here.
from importlib import import_module

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.template import loader
from django.utils.text import slugify
from django.utils import timezone

from reversion.models import Version
from reversion import revisions as reversion

from src.documents.models import Document
from src.utils.viewutils import render_pdf_context
from src.notifications.constants import SAFETY_TYPE_CHOICES
from src.notifications.managers import NotificationManager
from src.authorization.managers import AuthorizationManager
# from src.notifications.forms import NotificationForm
# import importlib
# model_module = importlib.import_module('src.notifications.forms')
# NotificationForm = getattr(model_module, 'NotificationForm')


class NotificationType(models.Model):
    #from .forms import NotificationForm
    name = models.CharField(max_length=80, unique=True)
    form = models.CharField(max_length=80, default='src.notifications.forms.NotificationForm')
    default_response = models.TextField(blank=True)
    position = models.IntegerField(default=0)

    includes_diff = models.BooleanField(default=False)
    grants_vote_extension = models.BooleanField(default=False)
    finishes_study = models.BooleanField(default=False)
    is_rejectable = models.BooleanField(default=False)
    
    @property
    def form_cls(self):
        if not hasattr(self, '_form_cls'):
            module, cls_name = self.form.rsplit('.', 1)
            self._form_cls = getattr(import_module(module), cls_name)
        return self._form_cls
        
    def get_template(self, pattern):
        template_names = [pattern % name for name in (self.form_cls.__name__, 'base')]
        return loader.select_template(template_names)
    
    def __str__(self):
        return self.name
    class Meta:
        app_label = 'notifications'
        #abstract = True


class DiffNotification(models.Model):
    old_submission_form = models.ForeignKey('core.SubmissionForm', related_name="old_for_notification", on_delete=models.CASCADE)
    new_submission_form = models.ForeignKey('core.SubmissionForm', related_name="new_for_notification", on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
        
    def save(self, **kwargs):
        super().save()
        self.submission_forms.set([self.old_submission_form])
        self.new_submission_form.is_transient = False
        self.new_submission_form.save(update_fields=('is_transient',))
        
    def apply(self):
        new_sf = self.new_submission_form
        if not self.new_submission_form.is_current and self.old_submission_form.is_current:
            new_sf.acknowledge(True)
            new_sf.mark_current()
            return True
        else:
            return False

    def get_diff(self, plainhtml=False):
        from core.diff import diff_submission_forms
        return diff_submission_forms(self.old_submission_form, self.new_submission_form).html(plain=plainhtml)


class Notification(models.Model):
    type = models.ForeignKey(NotificationType,blank=True, null=True, related_name='notifications', on_delete=models.SET_NULL)
    submission_forms = models.ManyToManyField('core.SubmissionForm', related_name='notifications')#---------------------------'core.'
    documents = models.ManyToManyField('documents.Document', related_name='notifications')
    pdf_document = models.OneToOneField(Document, related_name='_notification', null=True, on_delete=models.SET_NULL)

    comments = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)#   'auth.User'
    
    objects = NotificationManager()
    unfiltered = models.Manager()
    
    def __str__(self):
        return '{} für {}'.format(
            self.short_name,
            ' + '.join(str(sf.submission) for sf in self.submission_forms.all())
        )

    @property
    def short_name(self):
        sn = getattr(self, 'safetynotification', None)
        if sn:
            return sn.get_safety_type_display()
        return self.type.name

    @property
    def is_rejected(self):
        try:
            return self.answer.is_rejected
        except NotificationAnswer.DoesNotExist:
            return None

    def get_submission_form(self):
        if self.submission_forms.exists():
            return self.submission_forms.all()[0]
        return None

    def get_submission(self):
        sf = self.get_submission_form()
        if sf:
            return sf.submission
        return None
            
    def get_filename(self, suffix='.pdf'):
        ec_num = '_'.join(
            str(num)
            for num in self.submission_forms
                .order_by('submission__ec_number')
                .distinct()
                .values_list('submission__ec_number', flat=True)
        )
        base = '{}-{}'.format(slugify(ec_num), slugify(self.type.name))
        return base[:(250 - len(suffix))] + suffix

    def render_pdf(self):
        tpl = self.type.get_template('notifications/pdf/%s.html')
        submission_forms = self.submission_forms.select_related('submission')
        return render_pdf_context(tpl, {
            'notification': self,
            'submission_forms': submission_forms,
            'documents': self.documents.order_by('doctype__identifier', 'date', 'name'),
        })

    def render_pdf_document(self):
        assert self.pdf_document is None
        pdfdata = self.render_pdf()
        self.pdf_document = Document.objects.create_from_buffer(pdfdata,
            doctype='notification', parent_object=self, name=str(self)[:250],
            original_file_name=self.get_filename())
        self.save()
    class Meta:
        app_label = 'notifications'
        #abstract = True


class ReportNotification(Notification):
    study_started = models.BooleanField(default=True)
    reason_for_not_started = models.TextField(null=True, blank=True)
    recruited_subjects = models.PositiveIntegerField(null=True, blank=False)
    finished_subjects = models.PositiveIntegerField(null=True, blank=False)
    aborted_subjects = models.PositiveIntegerField(null=True, blank=False)
    SAE_count = models.PositiveIntegerField(default=0, blank=False)
    SUSAR_count = models.PositiveIntegerField(default=0, blank=False)
    
    class Meta:
        abstract = True
    

class CompletionReportNotification(ReportNotification):
    study_aborted = models.BooleanField(default=False)
    completion_date = models.DateField()
    class Meta:
        app_label = 'notifications'
        #abstract = True


class ProgressReportNotification(ReportNotification):
    runs_till = models.DateField(null=True, blank=True)
    class Meta:
        app_label = 'notifications'
        #abstract = True


class AmendmentNotification(DiffNotification, Notification):
    is_substantial = models.BooleanField(default=False)
    meeting = models.ForeignKey('meetings.Meeting', null=True,
        related_name='amendments', on_delete=models.SET_NULL)
    needs_signature = models.BooleanField(default=False)

    def schedule_to_meeting(self):
        from meetings.models import Meeting
        meeting = Meeting.objects.filter(started=None).order_by('start').first()
        self.meeting = meeting
        self.save()
    class Meta:
        app_label = 'notifications'
        #abstract = True


class SafetyNotification(Notification):
    safety_type = models.CharField(max_length=6, db_index=True, choices=SAFETY_TYPE_CHOICES, verbose_name=_('Type'))
    class Meta:
        app_label = 'notifications'
        #abstract = True

class CenterCloseNotification(Notification):
    investigator = models.ForeignKey('core.Investigator', related_name="closed_by_notification", on_delete=models.CASCADE)
    close_date = models.DateField()
    class Meta:
        app_label = 'notifications'
        #abstract = True


@reversion.register(fields=('text',))
class NotificationAnswer(models.Model):
    notification = models.OneToOneField(Notification, related_name="answer", on_delete=models.CASCADE)
    text = models.TextField()
    is_valid = models.BooleanField(default=True)
    is_final_version = models.BooleanField(default=False, verbose_name=_('Proofread'))
    is_rejected = models.BooleanField(default=False, verbose_name=_('rate negative'))
    pdf_document = models.OneToOneField(Document, related_name='_notification_answer', null=True, on_delete=models.SET_NULL)
    signed_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
    
    objects = AuthorizationManager()
    unfiltered = models.Manager()

    @property
    def version_number(self):
        return Version.objects.get_for_object(self).count()

    def get_render_context(self):
        return {
            'notification': self.notification,
            'documents': self.notification.documents.order_by('doctype__identifier', 'date', 'name'),
            'answer': self,
        }

    def render_pdf(self):
        notification = self.notification
        tpl = notification.type.get_template('notifications/answers/pdf/%s.html')
        return render_pdf_context(tpl, self.get_render_context())

    def render_pdf_document(self):
        pdfdata = self.render_pdf()
        self.pdf_document = Document.objects.create_from_buffer(pdfdata,
            doctype='notification_answer', parent_object=self,
            name=str(self),
            original_file_name=self.notification.get_filename('-answer.pdf')
        )
        self.save()
    
    def distribute(self):
        from core.models.submissions import Submission
        self.published_at = timezone.now()
        self.save()
        
        if not self.is_rejected and self.notification.type.includes_diff:
            try:
                notification = AmendmentNotification.objects.get(pk=self.notification.pk)
                notification.apply()
            except AmendmentNotification.DoesNotExist:
                assert False, "we should never get here"
        
        extend, finish = False, False
        if not self.is_rejected:
            if self.notification.type.grants_vote_extension:
                extend = True
            if self.notification.type.finishes_study:
                finish = True

        for submission in Submission.objects.filter(forms__in=self.notification.submission_forms.values('pk').query):
            if extend:
                for vote in submission.votes.positive().permanent():
                    vote.extend()
            if finish:
                submission.finish()
            presenting_parties = submission.current_submission_form.get_presenting_parties()
            _ = gettext
            presenting_parties.send_message(
                _('New Notification Answer'),
                'notifications/answers/new_message.txt',
                context={
                    'notification': self.notification,
                    'answer': self,
                    'ABSOLUTE_URL_PREFIX': settings.ABSOLUTE_URL_PREFIX,
                },
                submission=submission)
    class Meta:
        app_label = 'notifications'
        #abstract = True


NOTIFICATION_MODELS = (
    Notification, CompletionReportNotification, ProgressReportNotification,
    AmendmentNotification, SafetyNotification
)
