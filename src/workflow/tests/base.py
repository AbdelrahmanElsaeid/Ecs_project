from django.core import management
from src.utils.testcases import EcsTestCase
from src.workflow.controllers import clear_caches

class WorkflowTestCase(EcsTestCase):
    def setUp(self):
        super().setUp()
        clear_caches()
        management.call_command('workflow_sync')
        
    def tearDown(self):
        clear_caches()
        super().tearDown()

    def assertActivitiesEqual(self, obj, acts):
        self.assertEqual(set(acts), set(type(act) for act in obj.workflow.activities))

