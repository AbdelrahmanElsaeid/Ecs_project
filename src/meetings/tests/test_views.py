from datetime import datetime, timedelta
from urllib.parse import urlsplit

from django.urls import reverse
from django.contrib.auth.models import Group

from src.utils.testcases import EcsTestCase
from src.meetings.models import Meeting
from src.core.tests.test_submissions import create_submission_form

def _get_datetime_inputs(name, dt):
    return {
        '%s_0' % name: dt.strftime('%d.%m.%Y'),
        '%s_1' % name: dt.strftime("%H:%M"),
    }

class ViewTestCase(EcsTestCase):
    '''Tests for timetable and meetingassistant.
    
    Tests for Timetable calculations and storage,
    consistency of the meetingassistant's actions when starting and stopping meetings,
    quickjump feature. 
    '''
    
    def setUp(self):
        super().setUp()
        self.start = datetime(2020, 2, 20, 20, 20)
        self.user = self.create_user('unittest-office', profile_extra={'is_internal': True})
        self.user.groups.add(Group.objects.get(name='EC-Office'))
        self.client.login(email='unittest-office@example.com', password='password')

    def tearDown(self):
        self.client.logout()
        super().tearDown()

    def refetch(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def test_timetable(self):
        '''Tests if timetable durations are correct,
        and if meeting entries are correctly stored in the timetable.
        '''
        
        create_meeting_url = reverse('ecs.meetings.views.create_meeting')
        response = self.client.get(create_meeting_url)
        self.assertEqual(response.status_code, 200)

        data = {'title': 'Testmeeting'}
        data.update(_get_datetime_inputs('start', self.start))
        data.update(_get_datetime_inputs('deadline_diplomathesis', self.start + timedelta(days=30)))
        data.update(_get_datetime_inputs('deadline', self.start + timedelta(days=14)))
        response = self.client.post(create_meeting_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Meeting.objects.filter(start=self.start).count(), 1)
        meeting = Meeting.objects.get(start=self.start)
        
        timetable_url = reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': meeting.pk})
        response = self.client.get(timetable_url)
        self.assertEqual(response.status_code, 200)
        
        e0 = meeting.add_entry(duration=timedelta(seconds=42))
        response = self.client.post(reverse('ecs.meetings.views.update_timetable_entry', kwargs={'meeting_pk': meeting.pk, 'entry_pk': e0.pk}), {
            'duration': '2:00:00',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.refetch(e0).duration, timedelta(hours=2))
        
        e1 = meeting.add_entry(duration=timedelta(seconds=42))
        self.assertEqual(list(meeting), [e0, e1])
        
        response = self.client.get(reverse('ecs.meetings.views.move_timetable_entry', kwargs={'meeting_pk': meeting.pk}) + '?from_index=0&to_index=1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(self.refetch(meeting)), [e1, e0])
        
        response = self.client.get(reverse('ecs.meetings.views.remove_timetable_entry', kwargs={'meeting_pk': meeting.pk, 'entry_pk': e0.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(self.refetch(meeting)), [e1])
        

    def test_meeting_assistant(self):
        '''Makes sure that the meeting assistant is fully functional.
        Tests that the meeting assistant starts and stops meetings correctly.
        '''
        
        meeting = Meeting.objects.create(start=self.start)
        submission = create_submission_form().submission
        e0 = meeting.add_entry(duration=timedelta(seconds=42), submission=submission)
        e1 = meeting.add_entry(duration=timedelta(seconds=42*42))

        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_start', kwargs={'meeting_pk': meeting.pk}))
        self.assertEqual(response.status_code, 302)
        meeting = self.refetch(meeting)
        self.assertTrue(meeting.started)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}), {
            'close_top': 'on',
            'result': '1',
        })
        self.assertTrue(response.status_code, 302)
        self.assertFalse(self.refetch(e0).is_open)

        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_stop', kwargs={'meeting_pk': meeting.pk}))
        self.assertEqual(response.status_code, 404)

        response = self.client.post(reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e1.pk}), {
            'close_top': 'on',
            'result': '2',
        })
        self.assertTrue(response.status_code, 302)
        self.assertFalse(self.refetch(e1).is_open)
        
        response = self.client.get(reverse('ecs.meetings.views.meeting_assistant_stop', kwargs={'meeting_pk': meeting.pk}))
        self.assertEqual(response.status_code, 302)
        meeting = self.refetch(meeting)
        self.assertTrue(meeting.ended)

    def test_meeting_assistant_quickjump(self):
        '''Tests that the quickjump view is accessible and that it returns the right url.
        '''
        
        meeting = Meeting.objects.create(start=self.start, started=self.start)
        e0 = meeting.add_entry(duration=timedelta(seconds=42))
        e1 = meeting.add_entry(duration=timedelta(seconds=42*42))
        
        quickjump_url = reverse('ecs.meetings.views.meeting_assistant_quickjump', kwargs={'meeting_pk': meeting.pk})
        response = self.client.get(quickjump_url + '?q=')
        self.assertTrue(response.status_code, 200)
        
        response = self.client.get(quickjump_url + '?q=TOP 1', follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(status_code, 302)
        self.assertEqual(urlsplit(last_url).path, reverse('ecs.meetings.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': e0.pk}))
