from datetime import timedelta

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import F, Func

from celery import Celery
# from celery import periodic_task
from celery.schedules import crontab

from src.votes.models import Vote
from src.core.models.constants import SUBMISSION_LANE_LOCALEC
from src.users.utils import get_user, get_office_user
from src.communication.utils import send_message_template
from src.votes.constants import PERMANENT_VOTE_RESULTS


from celery import shared_task


WEEKLY_DOWNLOAD_THRESHOLD = 150

@shared_task
def send_vote_reminder(vote, subject, template, recipients):
    sender = get_user('root@system.local')
    submission = vote.get_submission()
    subject = subject.format(ec_number=submission.get_ec_number_display())
    template = 'votes/messages/{}'.format(template)
    for recipient in recipients:
        send_message_template(sender, recipient, subject, template, {
            'vote': vote,
            'submission': submission,
        }, submission=submission)

@shared_task
def send_vote_expired(vote):
    sf = vote.get_submission().current_submission_form
    recipients = sf.get_presenting_parties().get_users()
    recipients.add(get_office_user())
    subject = _('Vote for Submission {ec_number} has expired')
    send_vote_reminder(vote, subject, 'expired.txt', recipients)

@shared_task
def send_vote_reminder_submitter(vote):
    sf = vote.get_submission().current_submission_form
    recipients = sf.get_presenting_parties().get_users()
    subject = _('Vote for Submission {ec_number} will expire in three weeks')
    send_vote_reminder(vote, subject, 'reminder_submitter.txt', recipients)

@shared_task
def send_vote_reminder_office(vote):
    recipients = [get_office_user()]
    subject = _('Vote for Submission {ec_number} will expire in one week')
    send_vote_reminder(vote, subject, 'reminder_office.txt', recipients)

@shared_task
def send_temporary_vote_reminder_submitter(vote):
    sf = vote.get_submission().current_submission_form
    recipients = sf.get_presenting_parties().get_users()
    subject = _('Temporary vote for Submission {ec_number}')
    send_vote_reminder(vote, subject, 'temporary_reminder_submitter.txt', recipients)

@shared_task
def send_temporary_vote_reminder(vote):
    sf = vote.get_submission().current_submission_form
    recipients = sf.get_presenting_parties().get_users()
    recipients.add(get_office_user())
    subject = _('Temporary vote for Submission {ec_number}')
    send_vote_reminder(vote, subject, 'temporary_reminder.txt', recipients)

@shared_task
def send_reminder_messages(today=None):
    if today is None:
        today = timezone.now().date()

    votes = (
        Vote.objects
        .filter(published_at__isnull=False, valid_until__isnull=False)
        .exclude(submission_form__submission__workflow_lane=SUBMISSION_LANE_LOCALEC)
        .exclude(submission_form__submission__is_finished=True)
        .annotate(valid_until_date=Func(F('valid_until'), function='DATE'))
    )

    for vote in votes.filter(valid_until_date=Func(today + timedelta(days=21), function='DATE')):
        assert vote.result == '1'
        send_vote_reminder_submitter(vote)

    for vote in votes.filter(valid_until_date=Func(today + timedelta(days=7), function='DATE')):
        assert vote.result == '1'
        send_vote_reminder_office(vote)

    for vote in votes.filter(valid_until_date=Func(today - timedelta(days=1), function='DATE')):
        assert vote.result == '1'
        send_vote_expired(vote)

    tmp_votes = (
        Vote.objects
        .exclude(result__in=PERMANENT_VOTE_RESULTS)
        .exclude(_currently_published_for=None)
        .annotate(published_date=Func(F('published_at'), function='DATE'))
    )

    for vote in tmp_votes.filter(published_date=Func(today - timedelta(days=183), function='DATE')):
        send_temporary_vote_reminder_submitter(vote)

    for vote in tmp_votes.filter(published_date=Func(today - timedelta(days=365), function='DATE')):
        send_temporary_vote_reminder(vote)

@shared_task
def expire_votes():
    now = timezone.now()
    for vote in Vote.objects.filter(valid_until__lt=now, is_expired=False):
        vote.expire()


# def send_vote_reminder(vote, subject, template, recipients):
#     sender = get_user('root@system.local')
#     submission = vote.get_submission()
#     subject = subject.format(ec_number=submission.get_ec_number_display())
#     template = 'votes/messages/{}'.format(template)
#     for recipient in recipients:
#         send_message_template(sender, recipient, subject, template, {
#             'vote': vote,
#             'submission': submission,
#         }, submission=submission)


# def send_vote_expired(vote):
#     sf = vote.get_submission().current_submission_form
#     recipients = sf.get_presenting_parties().get_users()
#     recipients.add(get_office_user())

#     subject = _('Vote for Submission {ec_number} has expired')
#     send_vote_reminder(vote, subject, 'expired.txt', recipients)


# def send_vote_reminder_submitter(vote):
#     sf = vote.get_submission().current_submission_form
#     recipients = sf.get_presenting_parties().get_users()

#     subject = _('Vote for Submission {ec_number} will expire in three weeks')
#     send_vote_reminder(vote, subject, 'reminder_submitter.txt', recipients)

    
# def send_vote_reminder_office(vote):
#     recipients = [get_office_user()]

#     subject = _('Vote for Submission {ec_number} will expire in one week')
#     send_vote_reminder(vote, subject, 'reminder_office.txt', recipients)


# def send_temporary_vote_reminder_submitter(vote):
#     sf = vote.get_submission().current_submission_form
#     recipients = sf.get_presenting_parties().get_users()

#     subject = _('Temporary vote for Submission {ec_number}')
#     send_vote_reminder(vote, subject, 'temporary_reminder_submitter.txt', recipients)


# def send_temporary_vote_reminder(vote):
#     sf = vote.get_submission().current_submission_form
#     recipients = sf.get_presenting_parties().get_users()
#     recipients.add(get_office_user())

#     subject = _('Temporary vote for Submission {ec_number}')
#     send_vote_reminder(vote, subject, 'temporary_reminder.txt', recipients)


# # run once per day at 09:00
# @periodic_task(run_every=crontab(hour=9, minute=0))
# def send_reminder_messages(today=None):
#     if today is None:
#         today = timezone.now().date()


#     votes = (Vote.objects
#         .filter(published_at__isnull=False, valid_until__isnull=False)
#         .exclude(submission_form__submission__workflow_lane=SUBMISSION_LANE_LOCALEC)
#         .exclude(submission_form__submission__is_finished=True)
#         .annotate(valid_until_date=Func(F('valid_until'), function='DATE')))

#     for vote in votes.filter(
#             valid_until_date=Func(today + timedelta(days=21), function='DATE')):
#         assert vote.result == '1'
#         send_vote_reminder_submitter(vote)

#     for vote in votes.filter(
#             valid_until_date=Func(today + timedelta(days=7), function='DATE')):
#         assert vote.result == '1'
#         send_vote_reminder_office(vote)

#     for vote in votes.filter(
#             valid_until_date=Func(today - timedelta(days=1), function='DATE')):
#         assert vote.result == '1'
#         send_vote_expired(vote)


#     tmp_votes = (Vote.objects
#         .exclude(result__in=PERMANENT_VOTE_RESULTS)
#         .exclude(_currently_published_for=None)
#         .annotate(published_date=Func(F('published_at'), function='DATE')))

#     for vote in tmp_votes.filter(
#             published_date=Func(today - timedelta(days=183), function='DATE')):
#         send_temporary_vote_reminder_submitter(vote)

#     for vote in tmp_votes.filter(
#             published_date=Func(today - timedelta(days=365), function='DATE')):
#         send_temporary_vote_reminder(vote)

# # run once per day at 03:58
# @periodic_task(run_every=crontab(hour=3, minute=58))
# def expire_votes():
#     now = timezone.now()
#     for vote in Vote.objects.filter(valid_until__lt=now, is_expired=False):
#         vote.expire()
