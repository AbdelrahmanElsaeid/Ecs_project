from django.urls import reverse
from src.utils.testcases import LoginTestCase, EcsTestCase

class ImportTest(EcsTestCase):
    ''' Check if base and core urls,view,models are importable '''
    
    def test_import(self):
        "Tests if the urls module and core.urls, core.views, core.models are importable"
        
        import src.urls
        import src.core.urls
        import src.core.views
        import src.core.models
        
class CoreUrlsTest(LoginTestCase):
    '''High level tests for accessibility of core views of the system.'''
    
    def test_index(self):
        '''Tests if the Dashboard/main-site of the system is accessible.'''
        
        response = self.client.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_submission_forms(self):
        '''Tests if the all-submissions view of the system is accessible.'''
        
        response = self.client.get(reverse('ecs.core.views.submissions.all_submissions'))
        self.assertEqual(response.status_code, 200)

