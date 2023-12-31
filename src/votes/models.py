from datetime import timedelta

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from reversion.models import Version
from reversion import revisions as reversion

from src.votes.constants import (VOTE_RESULT_CHOICES, POSITIVE_VOTE_RESULTS, NEGATIVE_VOTE_RESULTS, PERMANENT_VOTE_RESULTS, RECESSED_VOTE_RESULTS)
from src.votes.managers import VoteManager
from src.votes.signals import on_vote_publication
from src.users.utils import get_current_user
from src.documents.models import Document
from src.utils.viewutils import render_pdf_context
from src.tasksv.models import Task


# @reversion.register(fields=('result', 'text'))
class Vote(models.Model):
    submission_form = models.ForeignKey('core.SubmissionForm', related_name='votes', on_delete=models.CASCADE)
    top = models.OneToOneField('meetings.TimetableEntry', related_name='vote', null=True,blank=True, on_delete=models.CASCADE)
    upgrade_for = models.OneToOneField('self', null=True,blank=True, related_name='previous', on_delete=models.CASCADE)
    result = models.CharField(max_length=2, choices=VOTE_RESULT_CHOICES, null=True, verbose_name=_('vote'))
    executive_review_required = models.BooleanField(blank=True, null=True)
    text = models.TextField(blank=True, verbose_name=_('comment'))
    is_draft = models.BooleanField(default=False)
    is_final_version = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True)
    published_at = models.DateTimeField(null=True)
    published_by = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    valid_until = models.DateTimeField(null=True)
    changed_after_voting = models.BooleanField(default=False)
    
    objects = VoteManager()
    unfiltered = models.Manager()

    class Meta:
        app_label = 'votes'
        get_latest_by = 'published_at'
        #abstract = True

    def get_submission(self):
        return self.submission_form.submission
    
    @property
    def result_text(self):
        # FIXME: use get_result_display instead
        if self.result is None:
            return _('No Result')
        return dict(VOTE_RESULT_CHOICES)[self.result]

    def get_ec_number(self):
        return self.submission_form.submission.get_ec_number_display()
        
    def __str__(self):
        if self.result in ('1', '4'):
            name = 'Votum'
        else:
            name = 'Mitteilung'

        ec_number = self.get_ec_number()
        if ec_number:
            return '{} {}'.format(name, ec_number)
        return '{} ID {}'.format(name, self.pk)

    def publish(self):
        assert self.published_at is None
        self.published_at = timezone.now()
        self.published_by = get_current_user()
        if self.result == '1':
            self.valid_until = self.published_at + timedelta(days=365)
        self.save()

        if not self.needs_signature:
            pdf_data = self.render_pdf()
            Document.objects.create_from_buffer(pdf_data, doctype='votes',
                parent_object=self, original_file_name=self.pdf_filename,
                name=str(self))

        submission = self.get_submission()
        assert submission.current_pending_vote_id == self.id
        submission.current_pending_vote = None
        submission.current_published_vote = self
        submission.save(
            update_fields=('current_pending_vote', 'current_published_vote'))

        on_vote_publication.send(sender=Vote, vote=self)

    def expire(self):
        assert not self.is_expired
        self.is_expired = True
        self.save()

        submission = self.get_submission()
        submission.is_expired = True
        submission.save(update_fields=('is_expired',))

        Task.unfiltered.for_submission(submission).filter(
            task_type__is_dynamic=True).open().mark_deleted()
    
    def extend(self):
        self.valid_until += timedelta(days=365)
        self.is_expired = False
        self.save()

        submission = self.get_submission()
        submission.is_expired = False
        submission.save(update_fields=('is_expired',))

    @property
    def version_number(self):
        return Version.objects.get_for_object(self).count()
    
    @property
    def is_positive(self):
        return self.result in POSITIVE_VOTE_RESULTS
        
    @property
    def is_negative(self):
        return self.result in NEGATIVE_VOTE_RESULTS
        
    @property
    def is_permanent(self):
        return self.result in PERMANENT_VOTE_RESULTS
        
    @property
    def is_recessed(self):
        return self.result in RECESSED_VOTE_RESULTS

    @property
    def needs_signature(self):
        return self.result in ('1', '4')

    @property
    def pdf_filename(self):
        vote_name = self.get_ec_number().replace('/', '-')
        if self.top:
            top = str(self.top)
            meeting = self.top.meeting
            filename = '{}-{}-{}-vote_{}.pdf'.format(meeting.title,
                timezone.localtime(meeting.start).strftime('%d-%m-%Y'),
                top, vote_name)
        else:
            filename = 'vote_{}.pdf'.format(vote_name)
        return filename.replace(' ', '_')

    def get_render_context(self):
        past_votes = Vote.objects.filter(published_at__isnull=False, submission_form__submission=self.submission_form.submission).exclude(pk=self.pk).order_by('published_at')

        return {
            'vote': self,
            'submission': self.get_submission(),
            'form': self.submission_form,
            'documents': self.submission_form.documents.order_by('doctype__identifier', 'date', 'name'),
            'ABSOLUTE_URL_PREFIX': settings.ABSOLUTE_URL_PREFIX,
            'past_votes': past_votes,
        }

    def render_pdf(self):
        return render_pdf_context('votes/pdf/vote.html',
            self.get_render_context())


@receiver(post_save, sender=Vote)
def _post_vote_save(sender, **kwargs):
    vote = kwargs['instance']
    submission = vote.submission_form.submission
    if not vote.published_at and submission.current_pending_vote != vote:
        submission.current_pending_vote = vote
        submission.save(update_fields=('current_pending_vote',))
