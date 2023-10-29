from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from staff.models import Recruitment

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
    content_type: ContentType = ContentType.objects.get_for_model(Recruitment)
    perms: list[Permission] = Permission.objects.filter(content_type=content_type, codename__in=permissions)
    group.permissions.set(perms)
    return group

class ServiceManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.user: User = create_user()
        self.group: Group = create_group('Service Manager', ['add_recruitment', 'delete_recruitment', 'view_recruitment', 'change_recruitment'])
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the add_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.add_recruitment'))

    def test_user_has_delete_permission(self) -> None:
        """
        Test that the user has the delete_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.delete_recruitment'))

    def test_user_has_view_permission(self) -> None:
        """
        Test that the user has the view_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.view_recruitment'))

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the change_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.change_recruitment'))

    def test_view_recruitment(self) -> None:
        """
        Test that Service Manager can view recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description',
        )
        self.assertEqual(recruitment._status, 'pending_hr_approval')
        response = self.client.get('/staff/recruitment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_delete_recruitment(self) -> None:
        """
        Test that Service Manager can delete recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description',
        )
        self.assertEqual(recruitment._status, 'pending_hr_approval')
        response = self.client.post(f'/staff/recruitment/{recruitment.pk}/delete/', {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Recruitment.objects.count(), 0)

    def test_change_recruitment(self) -> None:
        """
        Test that Service Manager can change recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description',
        )
        self.assertEqual(recruitment._status, 'pending_hr_approval')
        recruitment._status = 'pending_manager_approval'
        recruitment.save()
        response = self.client.get(f'/staff/recruitment/{recruitment.pk}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')
        self.assertEqual(recruitment._status, 'approved')

    def test_add_recruitment(self) -> None:
        """
        Test that Service Manager can add recruitment
        """
        response = self.client.post(f'/staff/recruitment/add/',
                                    {
                                        'contract_type': 'full',
                                        'requester': self.user.pk,
                                        'requesting_department': 'services',
                                        'years_of_experience': 5,
                                        'job_title': 'Test Job',
                                        'job_description': 'Test Job Description',
                                        '_save': 'Save',
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Recruitment.objects.count(), 1)

class HRTestCase(TestCase):
    def setUp(self) -> None:
        self.user: User = create_user()
        self.group: Group = create_group('HR', ['view_recruitment', 'change_recruitment'])
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the add_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.change_recruitment'))

    def test_user_has_not_delete_permission(self) -> None:
        """
        Test that the user has the delete_recruitment permission
        """
        self.assertFalse(self.user.has_perm('staff.delete_recruitment'))

    def test_user_has_view_permission(self) -> None:
        """
        Test that the user has the view_recruitment permission
        """
        self.assertTrue(self.user.has_perm('staff.view_recruitment'))

    def test_user_has_not_add_permission(self) -> None:
        """
        Test that the user has the add_recruitment permission
        """
        self.assertFalse(self.user.has_perm('staff.add_recruitment'))
    
    def test_cannot_add_recruitment(self) -> None:
        """
        Test that HR can add recruitment
        """
        self.client.post(f'/staff/recruitment/add/',
                                    {
                                        'requester': self.user.pk,
                                        'requesting_department': 'services',
                                        'years_of_experience': 5,
                                        'job_title': 'Test Job',
                                        'job_description': 'Test Job Description',
                                    })
        self.assertEqual(Recruitment.objects.count(), 0)

    def test_view_recruitment(self) -> None:
        """
        Test that HR can view recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description',
        )
        self.assertEqual(recruitment._status, 'pending_hr_approval')
        response = self.client.get('/staff/recruitment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

    def test_cannot_view_not_pending_recruitment(self) -> None:
        """
        Test that HR cannot view not pending hr recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description',
            _status = 'pending_manager_approval',
        )
        response = self.client.get('/staff/recruitment/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Job')


    def test_cannot_delete_recruitment(self) -> None:
        """
        Test that HR can delete recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description'
        )
        self.client.post(f'/staff/recruitment/{recruitment.pk}/delete/', {'post': 'yes'})
        self.assertEqual(Recruitment.objects.count(), 1)

    def test_can_change_recruitment(self) -> None:
        """
        Test that HR can change recruitment
        """
        recruitment: Recruitment = Recruitment.objects.create(
            requester=self.user,
            requesting_department='services',
            years_of_experience=5,
            job_title='Test Job',
            job_description='Test Job Description'
        )
        self.assertEqual(recruitment._status, 'pending_hr_approval')
        response = self.client.post(f'/staff/recruitment/{recruitment.pk}/change/',
                                    {
                                        'contract_type': 'full',
                                        'requester': self.user.pk,
                                        'requesting_department': 'services',
                                        'years_of_experience': 5,
                                        'job_title': 'Test Job',
                                        'job_description': 'Test Job Description',
                                        '_save': 'Save',
                                    })
        self.assertEqual(response.status_code, 302)
        recruitment.refresh_from_db()
        self.assertEqual(recruitment._status, 'pending_manager_approval')