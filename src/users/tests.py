from django.test import TestCase
import re

from django.urls import reverse
from django.test.client import Client

from src.communication.testcases import MailTestCase
from src.workflow.tests import WorkflowTestCase
from src.utils.testcases import EcsTestCase
from src.users.utils import get_user, create_user
from src.core.bootstrap import auth_groups
# Create your tests here.



class RegistrationTest(MailTestCase, WorkflowTestCase):
    '''Tests for the user registration functionality
    
    High level tests for the user registration. 
    '''
    
    def test_registration(self):
        '''Tests the registration process by registering as a new user,
        following the link in the registration mail message,
        setting a password and comparing the provided user data afterwards.
        '''
        # create user workflow
        auth_groups()

        response = self.client.post(reverse('src.users.views.register'), {
            'gender': 'm',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new.user@example.org',
        })
        self.assertEqual(response.status_code, 200)
        mimetype, message = self.get_mimeparts(self.queue_get(0), "text", "html")[0]
        
        # XXX: how do we get the right url without knowing its path-prefix? (FMD1)
        match = re.search(rb'href="https?://[\w.]+(/activate/[^"]+)"', message)
        self.assertTrue(match)
        activation_url = match.group(1)
        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(activation_url, {
            'password': 'password',
            'password_again': 'password',
        })
        self.assertEqual(response.status_code, 200)
        user = get_user('new.user@example.org')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.profile.gender, 'm')
        self.assertTrue(user.check_password('password'))
        

class PasswordChangeTest(MailTestCase):
    '''Tests for password changing functionality
    
    High level tests for password changing and password reset functionality.
    '''
    
    def test_password_reset(self):
        '''Makes sure that a user can reset his password,
        by following the link in a password reset mail message,
        setting a new password and performing a test login with the newly set password.
        '''
        
        user = create_user('new.user@example.org')
        user.set_password('password')
        user.save()
        response = self.client.post(reverse('src.users.views.request_password_reset'), {
            'email': 'new.user@example.org',
        })
        self.assertEqual(response.status_code, 200)
        mimetype, message = self.get_mimeparts(self.queue_get(0), "text", "html")[0]
        
        # XXX: how do we get the right url without knowing its path-prefix? (FMD1)
        match = re.search(rb'href="https?://[^/]+(/password-reset/[^"]+)"', message)
        self.assertTrue(match)
        password_reset_url = match.group(1)
        response = self.client.get(password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        
        response = self.client.post(password_reset_url, {
            'new_password1': '12345678',
            'new_password2': '12345678',
        })
        self.assertEqual(response.status_code, 200)
        user = get_user('new.user@example.org')
        self.assertTrue(user.check_password('12345678'))
        
        response = self.client.get(password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse('form' in response.context)
        
    def test_password_change(self):
        '''Makes sure that a password can be changed, by changing a password and
        performing a test-login afterwards with the changed password.
        '''
        
        user = create_user('foobar@example.com')
        user.set_password('test')
        user.save()
        self.client.login(email='foobar@example.com', password='test')

        url = reverse('src.users.views.change_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {
            'old_password': 'test', 
            'new_password1': '12345678',
            'new_password2': '12345678',
        })
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        user = get_user('foobar@example.com')
        self.assertTrue(user.check_password('12345678'))
        
class MiddlewareTest(EcsTestCase):
    '''Tests for the user middleware
    
    High level tests for user middleware features such as single-login enforcement.
    '''
    
    def setUp(self, *args, **kwargs):
        testuser = create_user('testuser@example.com')
        testuser.set_password('4223')
        testuser.save()

        return super().setUp(*args, **kwargs)

    def test_single_login(self):
        '''makes sure that a single user can only be logged in
        with one single client at any given time.
        '''
        c1 = Client()
        c2 = Client()

        login_url = reverse('src.users.views.login')
        dashboard_url = reverse('src.dashboard.views.view_dashboard')

        response = c1.post(login_url, {'username': 'testuser@example.com', 'password': '4223'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(dashboard_url))

        # c1.login(email='testuser@example.com', password='4223')
        response = c1.get(dashboard_url)
        self.assertEqual(response.status_code, 200)

        response = c2.post(login_url, {'username': 'testuser@example.com', 'password': '4223'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(dashboard_url))
        # now, c1 has to be logged out, because of the single login restriction

        response = c2.get(dashboard_url)
        self.assertEqual(response.status_code, 200)

        response = c1.get(dashboard_url)
        self.assertEqual(response.status_code, 302)
        
