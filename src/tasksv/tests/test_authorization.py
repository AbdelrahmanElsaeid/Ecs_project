from django.contrib.auth.models import Group

from src.utils.testcases import EcsTestCase
from src.tasks.models import TaskType, Task
from src.users.utils import create_user


class AuthorizationTest(EcsTestCase):
    '''Test for the tasks module
    
    
    Tests for user authorizations and task assignment.
    '''
    
    def setUp(self):
        group_a = Group.objects.create(name='group-a')
        group_b = Group.objects.create(name='group-b')
        self.user_a = create_user('a@example.com')
        self.user_b = create_user('b@example.com')
        self.user_c = create_user('c@example.com')
        self.user_a.groups.add(group_a)
        self.user_b.groups.add(group_a, group_b)
        self.task_type_a = TaskType.objects.create(name='task-type-a')
        self.task_type_a.group = group_a
        self.task_type_b = TaskType.objects.create(name='task-type-b')
        self.task_type_b.group = group_b
        self.task_type_c = TaskType.objects.create(name='task-type-c')

    def test_simple_assignment(self):
        '''Makes sure that assigning tasks to users works correctly.
        Also makes sure that tasks cannot be assigned to unauthorized users.
        '''
        
        task = Task.objects.create(task_type=self.task_type_a)
        task.assign(self.user_a)
        task.assign(self.user_b)
        self.assertRaises(ValueError, task.assign, self.user_c)
        
        task = Task.objects.create(task_type=self.task_type_b)
        self.assertRaises(ValueError, task.assign, self.user_a)
        task.assign(self.user_b)
        self.assertRaises(ValueError, task.assign, self.user_c)
        
        task = Task.objects.create(task_type=self.task_type_c)
        task.assign(self.user_a)
        task.assign(self.user_b)
        task.assign(self.user_c)
