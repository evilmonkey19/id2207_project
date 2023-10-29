from django.test import TestCase
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from tasks.models import Task

def create_user(
    username: str = 'testuser',
    password: str = 'testpass',
) -> User:
    """
    Create a user for testing
    """
    return User.objects.create_user(
        username=username,
        password=password,
        is_staff=True,
    )

def create_group(group_name: str, permissions: list[str] = []) -> Group:
    """
    Create a group
    """
    group: Group = Group.objects.get_or_create(name=group_name)[0]
    content_type: ContentType = ContentType.objects.get_for_model(Task)
    perms: list[Permission] = Permission.objects.filter(content_type=content_type, codename__in=permissions)
    group.permissions.set(perms)
    return group

class ServiceManagerTestCase(TestCase):
    def setUp(self) -> None:
        """
        Set up test case
        """
        self.user: User = create_user()
        self.group: Group = create_group('Service Manager', ['change_task', 'view_task', 'add_task', 'delete_task'])
        self.user.groups.add(self.group)
        self.subteam_user: User = create_user('subteamuser', 'subteampass')
        self.subteam_group: Group = create_group('Subteam', ['change_task', 'view_task'])
        self.subteam_user.groups.add(self.subteam_group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_permission_to_create_events(self):
        """
        Test that user has permission to create events
        """
        self.assertTrue(self.user.has_perm('tasks.add_task'))

    def test_user_has_permission_to_view_events(self):
        """
        Test that user has permission to view events
        """
        self.assertTrue(self.user.has_perm('tasks.view_task'))

    def test_user_has_permission_to_change_events(self):
        """
        Test that user has permission to change events
        """
        self.assertTrue(self.user.has_perm('tasks.change_task'))

    def test_user_has_permission_to_delete_events(self):
        """
        Test that user has permission to delete events
        """
        self.assertTrue(self.user.has_perm('tasks.delete_task'))

    def test_user_can_create_events(self):
        """
        Test that user can create events
        """
        response = self.client.post('/tasks/task/add/', {
            'project_ref': 'Test Project',
            'description': 'Test Description',
            'group': self.subteam_group.pk,
            'assigned_to': self.subteam_user.pk,
            'priority': 'm',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    def test_user_can_view_events(self):
        """
        Test that user can view events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.subteam_group,
            assigned_to=self.subteam_user,
            priority='m',
        )
        response = self.client.get('/tasks/task/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.project_ref)

    def test_user_can_change_events(self):
        """
        Test that user can change events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.subteam_group,
            assigned_to=self.subteam_user,
            priority='m',
        )
        response = self.client.post(f'/tasks/task/{task.pk}/change/', {
            'project_ref': 'Test Project',
            'description': 'Test Description',
            'group': self.subteam_group.pk,
            'assigned_to': self.subteam_user.pk,
            'priority': 'm',
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.project_ref, 'Test Project')

    def test_user_can_delete_events(self):
        """
        Test that user can delete events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.subteam_group,
            assigned_to=self.subteam_user,
            priority='m',
        )
        response = self.client.post(f'/tasks/task/{task.pk}/delete/', {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 0)

class SubteamTestCase(TestCase):
    def setUp(self) -> None:
        """
        Set up test case
        """
        self.user: User = create_user()
        self.group: Group = create_group('Subteam', ['change_task', 'view_task'])
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_not_permission_to_create_events(self):
        """
        Test that user has not permission to create events
        """
        self.assertFalse(self.user.has_perm('tasks.add_task'))

    def test_user_has_permission_to_view_events(self):
        """
        Test that user has permission to view events
        """
        self.assertTrue(self.user.has_perm('tasks.view_task'))

    def test_user_has_permission_to_change_events(self):
        """
        Test that user has permission to change events.
        It needs the permission in order to pass it 
        back to the manager.
        """
        self.assertTrue(self.user.has_perm('tasks.change_task'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that user has not permission to delete events
        """
        self.assertFalse(self.user.has_perm('tasks.delete_task'))

    def test_user_cannot_create_events(self):
        """
        Test that user can create events
        """
        response = self.client.post('/tasks/task/add/', {
            'project_ref': 'Test Project',
            'description': 'Test Description',
            'group': self.group.pk,
            'assigned_to': self.user.pk,
            'priority': 'm',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Task.objects.count(), 0)

    def test_user_can_view_events(self):
        """
        Test that user can view events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.group,
            assigned_to=self.user,
            priority='m',
        )
        response = self.client.get('/tasks/task/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, task.project_ref)

    def test_user_cannot_view_events_assigned_to_other_users(self):
        """
        Test that user can view events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.group,
            assigned_to=create_user('otheruser', 'otherpass'),
            priority='m',
        )
        response = self.client.get('/tasks/task/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, task.project_ref)

    def test_user_cannot_change_events(self):
        """
        Test that user can change events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.group,
            assigned_to=self.user,
            priority='m',
        )
        response = self.client.post(f'/tasks/task/{task.pk}/change/', {
            'project_ref': 'Test Project',
            'description': 'Test Description',
            'group': self.group.pk,
            'assigned_to': self.user.pk,
            'priority': 'm',
        })
        self.assertEqual(response.status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.project_ref, 'Test Project')
        self.assertEqual(task._status, 'pending_manager_approval')

    def test_user_cannot_delete_events(self):
        """
        Test that user can delete events
        """
        task: Task = Task.objects.create(
            project_ref='Test Project',
            description='Test Description',
            group=self.group,
            assigned_to=self.user,
            priority='m',
        )
        response = self.client.post(f'/tasks/task/{task.pk}/delete/', {'post': 'yes'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Task.objects.count(), 1)
