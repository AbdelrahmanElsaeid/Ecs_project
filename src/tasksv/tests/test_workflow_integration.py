from django.contrib.contenttypes.models import ContentType
from src.workflow.models import Graph
from src import workflow
# test only models:
from src.workflow.tests.models import Foo
from src.workflow.tests import flow_declarations as decl
from src.workflow.tests import WorkflowTestCase

from src.tasks.models import Task, TaskType


class WorkflowIntegrationTest(WorkflowTestCase):
    '''Tests for the tasks and workflow module.
    
    Tests for tasktype consistency, task creation, task completion and the task-trail functioning. 
    '''
    
    def setUp(self):
        super().setUp()
        self.foo_ct = ContentType.objects.get_for_model(Foo)

        g = Graph.objects.create(content_type=self.foo_ct, auto_start=True)
        self.n_a = g.create_node(decl.A, start=True)
        self.n_x = g.create_node(workflow.patterns.Generic)
        self.n_b = g.create_node(decl.B, end=True)
        self.n_a.add_edge(self.n_x)
        self.n_x.add_edge(self.n_b)
        self.graph = g
        
    def test_task_types(self):
        '''Makes sure that only the correct task types exist and
        that the correct Excpetion is raised on Nonexistence.
        '''
        
        self.assertTrue(TaskType.objects.get(workflow_node=self.n_a))
        self.assertTrue(TaskType.objects.get(workflow_node=self.n_b))
        self.assertRaises(TaskType.DoesNotExist, TaskType.objects.get, workflow_node=self.n_x)
        
    def test_task_creation(self):
        '''Tests if the tasks are created properly if a model instance is created.
        '''
        
        obj = Foo.objects.create()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.assertEqual(tasks[0].task_type.workflow_node, self.n_a)
        self.assertRaises(Task.DoesNotExist, tasks.get, task_type__workflow_node=self.n_b)
        
        obj.workflow.do(decl.A)
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.assertEqual(tasks[0].task_type.workflow_node, self.n_b)
        self.assertRaises(Task.DoesNotExist, tasks.get, task_type__workflow_node=self.n_a)

    def test_task_done(self):
        '''Tests if a task can be done via the workflow model.
        '''
        
        obj = Foo.objects.create()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.assertEqual(tasks[0].task_type.workflow_node, self.n_a)
        
        tasks[0].done()
        
        tasks = Task.objects.for_data(obj).filter(closed_at=None)
        self.assertEqual(tasks[0].task_type.workflow_node, self.n_b)

    def test_task_trail(self):
        '''Tests if the task trail works correctly.
        '''
        
        obj = Foo.objects.create()
        a_task = Task.objects.filter(closed_at=None).get()
        obj.workflow.do(decl.A)
        b_task = Task.objects.filter(closed_at=None).get()
        self.assertEqual(set(b_task.trail), {a_task})

        
