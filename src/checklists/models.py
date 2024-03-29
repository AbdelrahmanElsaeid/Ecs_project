from uuid import uuid4

from django.db import models
from django.db.models import Q, F
from django.utils.translation import gettext as _, gettext_lazy
from django.utils.text import slugify

from reversion import revisions as reversion

from src.authorization.managers import AuthorizationManager
from src.documents.models import Document
from src.utils.viewutils import render_pdf_context
from src.users.utils import get_current_user

class ChecklistBlueprint(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=50, db_index=True, unique=True)
    multiple = models.BooleanField(default=False)
    reviewer_is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return _(self.name)

class ChecklistQuestion(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='questions', on_delete=models.CASCADE)
    number = models.CharField(max_length=5, db_index=True)
    index = models.IntegerField(db_index=True)
    text = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    is_inverted = models.BooleanField(default=False)
    requires_comment = models.BooleanField(default=False)

    class Meta:
        unique_together = (('blueprint', 'number'),)
        ordering = ('blueprint', 'index',)

    def __str__(self):
        return "%s: '%s'" % (self.blueprint, self.text)


CHECKLIST_STATUS_CHOICES = (
    ('new', gettext_lazy('New')),
    ('completed', gettext_lazy('Completed')),
    ('review_ok', gettext_lazy('Review OK')),
    ('review_fail', gettext_lazy('Review Failed')),
    ('dropped', gettext_lazy('Dropped')),
)

class Checklist(models.Model):
    blueprint = models.ForeignKey(ChecklistBlueprint, related_name='checklists', on_delete=models.CASCADE)
    submission = models.ForeignKey('core.Submission', related_name='checklists', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.user', on_delete=models.CASCADE)
    status = models.CharField(max_length=15, default='new', choices=CHECKLIST_STATUS_CHOICES)
    pdf_document = models.OneToOneField(Document, related_name="checklist", null=True, on_delete=models.CASCADE)
    last_edited_by = models.ForeignKey('auth.user', related_name='edited_checklists', on_delete=models.CASCADE)

    objects = AuthorizationManager()
    unfiltered = models.Manager()

    class Meta:
        unique_together = (('blueprint', 'submission', 'user'),)
    
    @property
    def short_name(self):
        if self.blueprint.multiple:
            u = get_current_user()
            print(f"u is ======{u}")
            s = self.submission
            print(f"s is ======{s}")
            sf = self.submission.current_submission_form
            print(f"sf is ======{sf}")
            presenting_parties = [
                s.presenter_id, s.susar_presenter_id,
                sf.submitter_id, sf.sponsor_id,
                *(inv.user_id for inv in sf.investigators.all())
            ]
            #print(f"user_id is ======{user_id}")
            name = _('Anonymous') if self.blueprint.reviewer_is_anonymous else str(self.last_edited_by)
            if  (u is not None and u.profile.is_internal and not u.id in presenting_parties):
                name = str(self.last_edited_by)
            return "%s (%s)" % (self.blueprint, name)
        return str(self.blueprint)

    def __str__(self):
        if not self.submission:
            return self.short_name
        return '%s für %s' % (self.short_name, str(self.submission))
   

        
    @property
    def is_complete(self):
        return not self.answers.filter(
            Q(answer=None) |
            Q(Q(comment=None) | Q(comment=''), question__requires_comment=True)
        ).exists()

    @property
    def is_positive(self):
        return not self.answers.filter(question__is_inverted=F('answer')).exists()

    @property
    def is_negative(self):
        return not self.is_positive

    def get_answers_with_comments(self, answer=None):
        if answer is None:
            q = Q(answer=None)
        else:
            q = Q(question__is_inverted=False, answer=answer) | Q(question__is_inverted=True, answer=not answer)
        return self.answers.exclude(comment=None).exclude(comment="").filter(q).order_by('question')

    def get_all_answers_with_comments(self):
        return self.answers.exclude(comment=None).exclude(comment="").order_by('question')

    @property
    def has_positive_comments(self):
        return self.get_answers_with_comments(True).exists()

    @property
    def has_negative_comments(self):
        return self.get_answers_with_comments(False).exists()

    def render_pdf(self):
        return render_pdf_context('checklists/pdf/checklist.html', {
            'checklist': self,
        })

    def render_pdf_document(self):
        if self.blueprint.reviewer_is_anonymous:
            if self.submission:
                name = '{0} für {1}'.format(self.blueprint, self.submission)
            else:
                name = str(self.blueprint)
            name = '{0}-{1}'.format(name, uuid4().hex[:5])
        else:
            name = str(self)
        filename = '{0}.pdf'.format(slugify(name))

        pdfdata = self.render_pdf()
        self.pdf_document = Document.objects.create_from_buffer(pdfdata,
            doctype='checklist', parent_object=self, name=name,
            original_file_name=filename)
        self.save()

    def get_submission(self):
        return self.submission


@reversion.register(fields=('answer', 'comment'))
class ChecklistAnswer(models.Model):
    checklist = models.ForeignKey(Checklist, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(ChecklistQuestion, on_delete=models.CASCADE)
    answer = models.BooleanField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('question__blueprint', 'question__index')

    def __str__(self):
        return "Answer to '%s': %s" % (self.question, self.answer)

    @property
    def is_answered(self):
        return self.answer is not None

    @property
    def is_positive(self):
        return (not self.question.is_inverted and self.answer) or (self.question.is_inverted and self.answer == False)

    @property
    def is_negative(self):
        return not self.is_positive
