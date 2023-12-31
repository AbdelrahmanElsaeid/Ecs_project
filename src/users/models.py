from django.db import models
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    last_password_change = models.DateTimeField(auto_now_add=True)
    is_phantom = models.BooleanField(default=False)
    is_indisposed = models.BooleanField(default=False)
    communication_proxy = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # denormalized from user groups for faster lookup
    is_board_member = models.BooleanField(default=False)
    is_resident_member = models.BooleanField(default=False)
    is_omniscient_member = models.BooleanField(default=False)
    is_executive = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False)
    can_have_tasks = models.BooleanField(default=False)
    can_have_open_tasks = models.BooleanField(default=False)

    # XXX: not backed by user groups
    is_testuser = models.BooleanField(default=False)

    session_key = models.CharField(max_length=40, null=True)

    GENDER_CHOICES = [
        ('f', _('Ms')),
        ('m', _('Mr')),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    title = models.CharField(max_length=30, blank=True)
    organisation = models.CharField(max_length=180, blank=True)
    jobtitle = models.CharField(max_length=130, blank=True)
    swift_bic = models.CharField(max_length=11, blank=True)
    iban = models.CharField(max_length=40, blank=True)

    address1 = models.CharField(max_length=60, blank=True)
    address2 = models.CharField(max_length=60, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    fax = models.CharField(max_length=45, blank=True)

    SIGNING_CONNECTOR_CHOICES = (
        ('bku', _('localbku')),
        ('onlinebku', _('onlinebku')),
        ('mobilebku', _('mobilebku')),
    )
    signing_connector = models.CharField(max_length=9, choices=SIGNING_CONNECTOR_CHOICES, default='onlinebku')
    forward_messages_after_minutes = models.PositiveIntegerField(null=False, blank=False, default=0)

    task_uids = ArrayField(models.CharField(max_length=100), default=list)

    def __str__(self):
        return str(self.user)

    def update_flags(self):
        groups = set(self.user.groups.values_list('name', flat=True))
        self.is_board_member = 'Board Member' in groups
        self.is_resident_member = 'Resident Board Member' in groups
        self.is_omniscient_member = 'Omniscient Board Member' in groups
        self.is_executive = 'EC-Executive' in groups
        self.is_internal = bool(groups & {
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
        })
        self.can_have_tasks = bool(groups & {
            'Board Member',
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
            'GCP Reviewer',
            'Insurance Reviewer',
            'Statistic Reviewer',
            'External Reviewer',
            'Specialist'
        })
        self.can_have_open_tasks = bool(groups & {
            'Board Member',
            'EC-Executive',
            'EC-Office',
            'EC-Signing',
            'GCP Reviewer',
            'Insurance Reviewer',
            'Statistic Reviewer',
        })

    @property
    def show_task_widget(self):
        tasks = self.user.tasks(manager='unfiltered').open().for_widget()
        return self.can_have_tasks or tasks.exists()
    class Meta:
        app_label = 'users'
        #abstract = True


class UserSettings(models.Model):
    user = models.OneToOneField(User, related_name='ecs_settings', on_delete=models.CASCADE, null=True)
    submission_filter_search = models.JSONField(null=True)
    submission_filter_all = models.JSONField(null=True)
    submission_filter_widget = models.JSONField(null=True)
    submission_filter_widget_internal = models.JSONField(null=True)
    submission_filter_mine = models.JSONField(null=True)
    submission_filter_assigned = models.JSONField(null=True)
    task_filter = models.TextField(null=True)
    useradministration_filter = models.JSONField(null=True)
    class Meta:
        app_label = 'users'
        #abstract = True

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:     
        UserProfile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def _post_user_save(sender, instance, created, raw, **kwargs):
#     if created and not raw:
#         UserProfile.objects.create(user=instance)
#         UserSettings.objects.create(user=instance)


class InvitationQuerySet(models.QuerySet):
    def new(self):
        return self.filter(is_used=False)


class InvitationManager(models.Manager.from_queryset(InvitationQuerySet)):
    def get_queryset(self):
        return InvitationQuerySet(self.model).distinct()


class Invitation(models.Model):
    user = models.ForeignKey(User, related_name='ecs_invitations', on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    is_used = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    objects = InvitationManager()
    class Meta:
        app_label = 'users'
        #abstract = True


LOGIN_HISTORY_TYPES = (
    ('login', _('login')),
    ('logout', _('logout')),
)

class LoginHistory(models.Model):
    type = models.CharField(max_length=32, choices=LOGIN_HISTORY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(protocol='ipv4')
    class Meta:
        app_label = 'users'
        #abstract = True
