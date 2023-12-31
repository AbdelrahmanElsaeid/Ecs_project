from django.db import models

# Create your models here.
from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone

from src.utils import cached_property
from src.workflow.models import Token, Node
from src.workflow.signals import token_received, token_consumed, token_marked_deleted
from src.authorization.managers import AuthorizationManager






#----------------------new code update 12/4/2023  -----------------------------
# 
#     
class TaskType(models.Model):
    name = models.CharField(max_length=100)
    workflow_node = models.OneToOneField(Node, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, related_name='task_types', null=True, on_delete=models.SET_NULL)
    is_delegatable = models.BooleanField(default=True)
    is_dynamic = models.BooleanField(default=False)
    class Meta:
        app_label = "tasksv"
    
    def __str__(self):
        if self.name:
            return _(self.name)
        elif self.workflow_node_id:
            return 'TaskType for %s' % self.workflow_node
        return 'TaskType <Anonymous>'

    @property
    def trans_name(self):
        return _(self.name)

class TaskQuerySet(models.QuerySet):
    def for_data(self, data):
        ct = ContentType.objects.get_for_model(type(data))
        return self.filter(content_type=ct, data_id=data.pk)
        
    def open(self):
        return self.filter(deleted_at=None, closed_at=None)

    def closed(self):
        return self.filter(deleted_at=None, closed_at__isnull=False)
        
    def mark_deleted(self):
        for t in self.all():
            t.mark_deleted()

    def acceptable_for_user(self, user):
        from src.core.models import Submission
        submissions = Submission.objects.exclude(biased_board_members=user)
        return self.for_submissions(submissions).filter(
            Q(assigned_to=None) | Q(assigned_to__profile__is_indisposed=True),
            deleted_at=None
        )

    def for_user(self, user):
        return self.filter(
            Q(task_type__group__user=user) | Q(task_type__group=None) | Q(assigned_to=user),
            deleted_at=None
        )

    def for_widget(self):
        return self.exclude(task_type__workflow_node__uid__in=(
            'resubmission',
            'b2_resubmission',
            'paper_submission_review',
        ))

    def for_submissions(self, submissions):
        from src.core.models import Submission
        from src.votes.models import Vote
        from src.checklists.models import Checklist
        from src.notifications.models import Notification, NOTIFICATION_MODELS

        submission_ct = ContentType.objects.get_for_model(Submission)
        q = Q(content_type=submission_ct, data_id__in=submissions)

        vote_ct = ContentType.objects.get_for_model(Vote)
        votes = Vote.objects.filter(submission_form__submission__in=submissions)
        q |= Q(content_type=vote_ct, data_id__in=votes.values('pk'))

        notification_cts = ContentType.objects.get_for_models(
            *NOTIFICATION_MODELS).values()
        notifications = Notification.objects.filter(
            submission_forms__submission__in=submissions)
        q |= Q(content_type__in=notification_cts,
            data_id__in=notifications.values('pk'))

        checklist_ct = ContentType.objects.get_for_model(Checklist)
        checklists = Checklist.objects.filter(submission__in=submissions)
        q |= Q(content_type=checklist_ct,
            data_id__in=checklists.values('pk'))
            
        return self.filter(q).distinct()

    def for_submission(self, submission):
        return self.for_submissions([submission.id])
    
class TaskManager(AuthorizationManager.from_queryset(TaskQuerySet)):
    def get_base_queryset(self):
        # XXX: We really shouldn't be using distinct() here - it hurts
        # performance.
        return TaskQuerySet(self.model).distinct()


class Task(models.Model):
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE, related_name='tasks')
    workflow_token = models.OneToOneField(Token, null=True, on_delete=models.CASCADE, related_name='task')
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    data_id = models.PositiveIntegerField(null=True)
    data = GenericForeignKey(ct_field='content_type', fk_field='data_id')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='created_tasks')

    assigned_at = models.DateTimeField(null=True)
    assigned_to = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='tasks')
    closed_at = models.DateTimeField(null=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, db_index=True)

    accepted = models.BooleanField(default=False)

    medical_category = models.ForeignKey('core.MedicalCategory', null=True, on_delete=models.SET_NULL)

    review_for = models.ForeignKey('self',blank=True, null=True, on_delete=models.SET_NULL)

    send_message_on_close = models.BooleanField(default=False)
    reminder_message_timeout = models.DurationField(null=True)
    reminder_message_sent_at = models.DateTimeField(null=True)
    objects = TaskManager()
    unfiltered = TaskQuerySet.as_manager()

    class Meta:
        app_label = "tasksv"
    def save(self, *args, **kwargs):
        rval = super().save(*args, **kwargs)
        if self.workflow_token and not self.workflow_token.deadline:
            self.workflow_token.deadline = timezone.now() + timedelta(days=30)
            self.workflow_token.save()
        return rval    
        
    def get_preview_url(self):
        from src.notifications.models import Notification

        if isinstance(self.data, Notification):
            return reverse('src.notifications.views.view_notification',
                kwargs={'notification_pk': self.data.pk})

        submission = self.data.get_submission()
        if not submission:
            return None

        return reverse('view_submission',
            kwargs={'submission_pk': submission.pk})

    @property
    def managed_transparently(self):
        return self.task_type.workflow_node.uid in ['resubmission', 'b2_resubmission', 'vote_signing']

    @property
    def is_locked(self):
        if not self.workflow_token_id:
            return False
        return self.workflow_token.locked
    
    @cached_property
    def node_controller(self):
        if not self.workflow_token_id:
            return None
        return self.workflow_token.node.bind(self.workflow_token.workflow)
        
    @cached_property
    def url(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_url()
        
    def get_final_urls(self):
        if not self.node_controller:
            return []
        return self.node_controller.get_final_urls()

    @cached_property
    def afterlife_url(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_afterlife_url()
    
    @property
    def choices(self):
        if not self.node_controller:
            return None
        return self.node_controller.get_choices()
    
    def close(self, commit=True):
        self.closed_at = timezone.now()
        if commit:
            self.save()

        if self.send_message_on_close:
            from src.tasksv.tasks import send_close_message
            send_close_message(self)
        
    def done(self, choice=None, user=None, commit=True):
        if user and self.assigned_to_id != user.id:
            self.assign(user)
        token = self.workflow_token
        if token:
            self.data.workflow.do(token, choice=choice)
        else:
            self.close(commit=commit)
    
    def mark_deleted(self, commit=True):
        assert self.deleted_at is None
        token = self.workflow_token
        if token:
            token.mark_deleted()
        else:
            self.deleted_at = timezone.now()
            if commit:
                self.save()
            
    def reopen(self, user=None):
        assert self.closed_at is not None or self.deleted_at is not None
        new = type(self)()
        for attr in ('task_type', 'content_type', 'data_id', 'medical_category_id'):
            setattr(new, attr, getattr(self, attr))
        user = user or self.assigned_to
        new.created_by = user
        new.accept(user=user, check_authorization=False)
        def _repeated_token_received(sender, **kwargs):
            if sender.repeated and sender.node == self.workflow_token.node:
                new.workflow_token = sender
                new.save()
        token_received.connect(_repeated_token_received)
        new.workflow_token = self.node_controller.activate(reopen=True)
        token_received.disconnect(_repeated_token_received)
        return new
        
    def assign(self, user, check_authorization=True, commit=True):
        if user and check_authorization:
            group = self.task_type.group
            if group and not user.groups.filter(pk=group.id).exists():
                raise ValueError(("Task %s cannot be assigned to user %s, it requires the following group: %s" % (
                    self, 
                    user, 
                    group,
                )).encode('ascii', 'ignore'))
        self.assigned_to = user
        self.accepted = False
        if user:
            self.assigned_at = timezone.now()
        else:
            self.assigned_at = None
        if commit:
            self.save()
        
    def accept(self, user=None, check_authorization=True):
        if user:
            self.assign(user, commit=False, check_authorization=check_authorization)
        self.accepted = True
        self.save()
        
    @property
    def trail(self):
        if not self.workflow_token:
            return Task.objects.none()
        return Task.objects.filter(workflow_token__in=self.workflow_token.activity_trail)

    def __str__(self):
        return "%s %s" % (self.data, self.task_type)

# workflow integration:
@receiver(token_received)
def workflow_token_received(sender, **kwargs):
    if sender.repeated:
        return
    try:
        task_type = TaskType.objects.get(workflow_node=sender.node)
        Task.objects.create(workflow_token=sender, task_type=task_type, data=sender.workflow.data)
    except TaskType.DoesNotExist:
        pass

@receiver(token_consumed)
def workflow_token_consumed(sender, **kwargs):
    for task in Task.unfiltered.filter(workflow_token=sender, closed_at=None):
        task.close()

@receiver(token_marked_deleted)
def workflow_token_marked_deleted(sender, **kwargs):
    for task in Task.unfiltered.filter(workflow_token=sender, deleted_at=None):
        task.deleted_at = timezone.now()
        task.save()

@receiver(post_save, sender=Node)
def node_saved(sender, **kwargs):
    node, created = kwargs['instance'], kwargs['created']
    if not created or not node.node_type.is_activity:
        return
    name = node.name or node.node_type.name or node.node_type.implementation
    task_type, created = TaskType.objects.get_or_create(workflow_node=node, name=name)    