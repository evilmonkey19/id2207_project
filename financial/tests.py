from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission

from financial.models import FinancialRequest

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
    content_type: ContentType = ContentType.objects.get_for_model(FinancialRequest)
    perms: list[Permission] = Permission.objects.filter(content_type=content_type, codename__in=permissions)
    group.permissions.set(perms)
    return group

class ServiceManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.user: User = create_user()
        self.group: Group = create_group('Service Manager', ['add_financialrequest', 'delete_financialrequest', 'view_financialrequest', 'change_financialrequest'])
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the add_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.add_financialrequest'))

    def test_user_has_delete_permission(self) -> None:
        """
        Test that the user has the delete_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.delete_financialrequest'))

    def test_user_has_view_permission(self) -> None:
        """
        Test that the user has the view_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.view_financialrequest'))

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the change_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.change_financialrequest'))

    def test_view_financial_request_list(self) -> None:
        """
        Test that the user can view the list of financial requests
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.get('/financial/financialrequest/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

    def test_delete_financial_request(self) -> None:
        """
        Test that the user can delete a financial request
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.post(f'/financial/financialrequest/{financial_request.pk}/delete/', { 'post': 'yes' })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialRequest.objects.count(), 0)

    def test_change_financial_request(self) -> None:
        """
        Test that the user can change a financial request
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.post(f'/financial/financialrequest/{financial_request.pk}/change/', {
            'requesting_department': 'services',
            'project_reference': 'test',
            'required_amount': 1000,
            'reason': 'test',
            '_status': 'approved',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialRequest.objects.count(), 1)
        financial_request.refresh_from_db()
        self.assertEqual(financial_request._status, 'approved')
        self.assertEqual(financial_request.requesting_department, 'services')
        self.assertEqual(financial_request.project_reference, 'test')
        self.assertEqual(financial_request.required_amount, 1000)
        self.assertEqual(financial_request.reason, 'test')

    def test_add_financial_request(self) -> None:
        """
        Test that the user can add a financial request
        """
        response = self.client.post(f'/financial/financialrequest/add/',
                                    {
                                        'requesting_department': 'services',
                                        'project_reference': 'test',
                                        'required_amount': 1000,
                                        'reason': 'test',
                                        '_status': 'approved',
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialRequest.objects.count(), 1)


class FinancialManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.user: User = create_user()
        self.group: Group = create_group('Financial Manager', ['view_financialrequest', 'change_financialrequest'])
        self.user.groups.add(self.group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_change_permission(self) -> None:
        """
        Test that the user has the add_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.change_financialrequest'))

    def test_user_has_not_delete_permission(self) -> None:
        """
        Test that the user has the delete_financialrequest permission
        """
        self.assertFalse(self.user.has_perm('financial.delete_financialrequest'))

    def test_user_has_view_permission(self) -> None:
        """
        Test that the user has the view_financialrequest permission
        """
        self.assertTrue(self.user.has_perm('financial.view_financialrequest'))

    def test_user_has_not_add_permission(self) -> None:
        """
        Test that the user has the add_financialrequest permission
        """
        self.assertFalse(self.user.has_perm('financial.add_financialrequest'))

    def test_cannot_add_financial_request(self) -> None:
        """
        Test that the user cannot add a financial request
        """
        response = self.client.post(f'/financial/financialrequest/add/',
                                    {
                                        'requesting_department': 'services',
                                        'project_reference': 'test',
                                        'required_amount': 1000,
                                        'reason': 'test',
                                        '_status': 'approved',
                                    })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FinancialRequest.objects.count(), 0)

    def test_view_financial_request_list(self) -> None:
        """
        Test that the user can view the list of financial requests
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.get('/financial/financialrequest/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test')

    def test_cannot_view_not_pending_financial_requests(self) -> None:
        """
        Test that the user cannot view the list of financial requests
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='testproject',
            required_amount=1000,
            _status='approved',
        )
        response = self.client.get('/financial/financialrequest/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'testproject')

    def test_cannot_delete_financial_request(self) -> None:
        """
        Test that the user cannot delete a financial request
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.post(f'/financial/financialrequest/{financial_request.pk}/delete/', { 'post': 'yes' })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(FinancialRequest.objects.count(), 1)

    def test_change_financial_request(self) -> None:
        """
        Test that the user can change a financial request
        """
        financial_request: FinancialRequest = FinancialRequest.objects.create(
            requesting_department='financial',
            project_reference='test',
            required_amount=1000,
        )
        self.assertEqual(financial_request._status, 'pending_financial_approval')
        response = self.client.post(f'/financial/financialrequest/{financial_request.pk}/change/', {
            'requesting_department': 'financial',
            'project_reference': 'test',
            'required_amount': 1000,
            'reason': 'test',
            '_status': 'approved',
            '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FinancialRequest.objects.count(), 1)
        financial_request.refresh_from_db()
        self.assertEqual(financial_request._status, 'approved')
        self.assertEqual(financial_request.requesting_department, 'financial')
        self.assertEqual(financial_request.project_reference, 'test')
        self.assertEqual(financial_request.required_amount, 1000)
        self.assertEqual(financial_request.reason, '')