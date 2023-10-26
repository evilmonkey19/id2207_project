from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.contrib.auth.models import Group, Permission, User
from events.models import Events

def create_user() -> User:
    """
    Create a user for testing
    """
    return User.objects.create_user(
        username='testuser',
        password='testpass'
    )

def add_user_to_group(user: User, group_name: str, permissions: list = []) -> None:
    """
    Add the user to a group
    """
    group, _ = Group.objects.get_or_create(name=group_name)
    for permission in permissions:
        content_type = ContentType.objects.get_for_model(Events)
        permission = Permission.objects.get(
            codename=permission,
            content_type=content_type,
        )
        group.permissions.add(permission)
    user.groups.add(group)

class EventsCustomerServiceTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        add_user_to_group(
            self.user,
            'Customer service',
            permissions=["add_events"]
        )


    def test_user_has_permission_to_create_events(self):
        """
        Test that the user has the add_events permission
        """
        self.assertTrue(self.user.has_perm('events.add_events'))

    def test_user_has_not_permission_to_change_events(self):
        """
        Test that the user has not the change_events permission
        """
        self.assertFalse(self.user.has_perm('events.change_events'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that the user has not the delete_events permission
        """
        self.assertFalse(self.user.has_perm('events.delete_events'))

class EventsSeniorCustomerServiceTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        add_user_to_group(
            self.user,
            'Senior customer service',
            permissions=["change_events", "approve_events", "delete_events",]
        )
    
    def test_user_has_permission_to_change_events(self):
        """
        Test that the user has the change_events permission
        """
        self.assertTrue(self.user.has_perm('events.change_events'))

    def test_user_has_permission_to_approve_events(self):
        """
        Test that the user has the approve_events permission
        """
        self.assertTrue(self.user.has_perm('events.approve_events'))

    def test_user_has_permission_to_delete_events(self):
        """
        Test that the user has the delete_events permission
        """
        self.assertTrue(self.user.has_perm('events.delete_events'))


class EventsFinancialManagerTestCase(TestCase):
    pass

class EventsAdministrationManagerTestCase(TestCase):
    pass

    