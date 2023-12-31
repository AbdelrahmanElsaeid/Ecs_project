from django.test import TestCase

# Create your tests here.
from contextlib import contextmanager
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from src.utils.testcases import EcsTestCase
from src.core.tests.test_submissions import create_submission_form
from src.core.models import Submission
from src.meetings.models import Meeting
from src.users.utils import sudo, create_user

class SubmissionAuthTestCase(EcsTestCase):
    '''Tests for the authorization- and role-management of all types of users regarding access to a submission.

    Tests the authorization to view a submission for each user-role.
    Also tests that a submission is not accessible in the system depending on the role of the user.
    '''
    
    BASE_EC_NUMBER = 9742
    EC_NUMBER = 20100000 + BASE_EC_NUMBER
    
    def _create_test_user(self, name, **profile_attrs):
        email = '{0}@example.com'.format(name)
        user = create_user(email)
        user.set_password(email)
        user.save()
        profile = user.profile
        for name, value in profile_attrs.items():
            setattr(profile, name, value)
        profile.save()
        return user
    
    def setUp(self):
        super().setUp()
        self.anyone = self._create_test_user('anyone')
        self.board_member_user = self._create_test_user('board_member', is_board_member=True)
        self.internal_user = self._create_test_user('internal', is_internal=True)
        self.primary_investigator_user = self._create_test_user('primary_investigator')
        self.sponsor_user = self._create_test_user('sponsor')
        self.submitter_user = self._create_test_user('submitter')
        self.another_board_member_user = self._create_test_user('another_board_member', is_board_member=True)
    
        sf = create_submission_form()
        sf.submitter = self.submitter_user
        sf.sponsor = self.sponsor_user
        sf.project_title = self.EC_NUMBER
        sf.save()
    
        investigator = sf.investigators.all()[0]
        investigator.user = self.primary_investigator_user
        investigator.save()

        sf.submission.ec_number = self.EC_NUMBER

        meeting = Meeting.objects.create(start=timezone.now())
        entry = meeting.add_entry(submission=sf.submission, duration=timedelta(seconds=60))
        entry.participations.create(user=self.board_member_user)
        sf.submission.next_meeting = meeting
        sf.submission.save()

        self.sf = sf
        
    def test_submission_auth(self):
        ''' Test that users can only see the submissions he/she is entitled to see.
        
        Makes sure that each user group (and status of a user to a submission) 
        only sees the submissions he/she is entitled to; Checked are role, status 
        and type of the user in relation to the submission (anyone, submitter,
        sponsor, investigator, etc. )
        '''
        
        with sudo(self.anyone):
            self.assertEqual(Submission.objects.count(), 0)
        with sudo(self.submitter_user):
            self.assertEqual(Submission.objects.count(), 1)
        with sudo(self.sponsor_user):
            self.assertEqual(Submission.objects.count(), 1)
        with sudo(self.primary_investigator_user):
            self.assertEqual(Submission.objects.count(), 1)
        with sudo(self.internal_user):
            self.assertEqual(Submission.objects.count(), 1)
        with sudo(self.board_member_user):
            self.assertEqual(Submission.objects.count(), 1)
        with sudo(self.another_board_member_user):
            self.assertEqual(Submission.objects.count(), 0)

    @contextmanager
    def _login(self, user):
        self.client.login(email=user.email, password=user.email)
        yield
        self.client.logout()
        
    def _check_access(self, allowed, expect404, user, url):
        with self._login(user):
            response = self.client.get(url)
            while response.status_code == 302:
                response = self.client.get(response['Location'])
            if expect404:
                self.assertEqual(response.status_code, allowed and 200 or 404)
            else:
                self.assertEqual(str(self.BASE_EC_NUMBER).encode('ascii') in response.content, allowed)
                
    def _check_view(self, expect404, viewname, *args, **kwargs):
        url = reverse(viewname, args=args, kwargs=kwargs)
        self._check_access(False, expect404, self.anyone, url)
        self._check_access(False, expect404, self.anyone, url)
        self._check_access(True, expect404, self.submitter_user, url)
        self._check_access(True, expect404, self.sponsor_user, url)
        self._check_access(True, expect404, self.primary_investigator_user, url)
        self._check_access(True, expect404, self.internal_user, url)
        self._check_access(True, expect404, self.board_member_user, url)
        self._check_access(False, expect404, self.another_board_member_user, url)

    def test_views(self):
        '''Tests that viewing all views related to a submission works for authorized users 
        and is denied for unauthorized users depending on the role of the users.
        '''
        
        self._check_view(False, 'ecs.core.views.submissions.all_submissions')
        self._check_view(False, 'readonly_submission_form', submission_form_pk=self.sf.pk)
        self._check_view(False, 'ecs.core.views.submissions.diff', self.sf.pk, self.sf.pk)

        export_url = reverse('ecs.core.views.submissions.export_submission', kwargs={'submission_pk': self.sf.submission.pk})
        self._check_access(False, True, self.anyone, export_url)
        self._check_access(False, True, self.submitter_user, export_url)
        self._check_access(False, True, self.sponsor_user, export_url)
        self._check_access(False, True, self.primary_investigator_user, export_url)
        self._check_access(True, True, self.internal_user, export_url)
        self._check_access(False, True, self.board_member_user, export_url)
        self._check_access(False, True, self.another_board_member_user, export_url)
        self._check_access(True, True, self.sf.submission.presenter, export_url)

        #self._check_view(True, 'ecs.documents.views.document_search', document_pk=self.sf.documents.all()[0].pk)
        #self._check_view('ecs.core.views.submissions.copy_submission_form', submission_form_pk=self.sf.pk)
        #self._check_view('ecs.core.views.submissions.copy_latest_submission_form', submission_pk=self.sf.submission.pk)