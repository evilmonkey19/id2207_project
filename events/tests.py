from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import TestCase
from django.contrib.auth.models import Group, Permission, User
from events.models import Event

def create_user() -> User:
    """
    Create a user for testing
    """
    return User.objects.create_user(
        username='testuser',
        password='testpass',
        is_staff=True,
    )

def create_group(group_name: str, permissions: list[str] = []) -> Group:
    """
    Create a group
    """
    group: Group = Group.objects.get_or_create(name=group_name)[0]
    content_type: ContentType = ContentType.objects.get_for_model(Event)
    perms: list[Permission] = Permission.objects.filter(content_type=content_type, codename__in=permissions)
    group.permissions.set(perms)
    return group

class CustomerServiceTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        group = create_group('Customer service', ["add_event"])
        self.user.groups.add(group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_permission_to_create_events(self):
        """
        Test that the user has the add_events permission
        """
        self.assertTrue(self.user.has_perm('events.add_event'))

    def test_user_has_not_permission_to_change_events(self):
        """
        Test that the user has not the change_events permission
        """
        self.assertFalse(self.user.has_perm('events.change_event'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that the user has not the delete_events permission
        """
        self.assertFalse(self.user.has_perm('events.delete_event'))

    def test_user_has_not_permission_to_view_events(self):
        """
        Test that the user has not the view_events permission
        """
        self.assertFalse(self.user.has_perm('events.view_event'))

    def test_user_can_create_event(self):
        """
        Test that the user can create an event
        """
        response = self.client.post('/events/event/add/', {
            'record_number': '',
            'client_name': 'Test Client',
            'event_type': 'Test Event',
            'from_date': '2021-01-01',
            'to_date': '2021-01-01',
            'attendes': 100,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 1000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        event: Event = Event.objects.first()
        self.assertEqual(event.client_name, 'Test Client')
        self.assertEqual(event.event_type, 'Test Event')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.attendes, 100)
        self.assertEqual(event.meals, True)
        self.assertEqual(event.drinks, True)
        self.assertEqual(event.expected_budget, 1000)

    def test_user_cannot_create_event_with_invalid_data(self):
        """
        Test that the user can not create an event with invalid data
        """
        response = self.client.post('/events/event/add/', {
            'client_name': '',
            'event_type': '',
            'from_date': '',
            'to_date': '',
            'attendes': '',
            'decorations': '',
            'meals': '',
            'drinks': '',
            'photos_filming': '',
            'parties': '',
            'expected_budget': '',
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)

    def test_user_cannot_search_events(self):
        """
        Test that the user can not search events
        """
        response = self.client.get('/events/event/')
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_change_events(self):
        """
        Test that the user can not change events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
        )
        response = self.client.get(f'/events/event/{event.id}/change/')
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_view_events(self):
        """
        Test that the user can not view events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            meals=True,
            drinks=True,
            expected_budget=1000,
        )
        response = self.client.get(f'/events/event/{event.id}/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_delete_events(self):
        """
        Test that the user can not delete events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            meals=True,
            drinks=True,
            expected_budget=1000,
        )
        response = self.client.post(f'/events/event/{event.id}/delete/', {
            'post': 'yes'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 1)


class SeniorCustomerServiceTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        group = create_group('Senior customer service', ["change_event", "view_event"])
        self.user.groups.add(group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_permission_to_change_events(self):
        """
        Test that the user has the change_events permission
        """
        self.assertTrue(self.user.has_perm('events.change_event'))

    def test_user_has_not_permission_to_create_events(self):
        """
        Test that the user has not the add_events permission
        """
        self.assertFalse(self.user.has_perm('events.add_event'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that the user has not the delete_events permission
        """
        self.assertFalse(self.user.has_perm('events.delete_event'))
    
    def test_user_has_permission_to_view_events(self):
        """
        Test that the user has the view_events permission
        """
        self.assertTrue(self.user.has_perm('events.view_event'))

    def test_user_can_change_event(self):
        """
        Test that the user can change an event
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'record_number': '',
            'client_name': 'Test Client 2',
            'event_type': 'Test Event 2',
            'from_date': '2021-01-02',
            'to_date': '2021-01-02',
            'attendes': 200,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 2000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client 2')
        self.assertEqual(event.event_type, 'Test Event 2')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-02')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-02')
        self.assertEqual(event.attendes, 200)
        self.assertEqual(event.meals, True)
        self.assertEqual(event.drinks, True)
        self.assertEqual(event.expected_budget, 2000)

    def test_user_cannot_change_event_with_invalid_data(self):
        """
        Test that the user can not change an event with invalid data
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'client_name': '',
            'event_type': '',
            'from_date': '',
            'to_date': '',
            'attendes': '',
            'decorations': '',
            'meals': '',
            'drinks': '',
            'photos_filming': '',
            'parties': '',
            'expected_budget': '',
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client')
        self.assertEqual(event.event_type, 'Test Event')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.attendes, 100)
        self.assertEqual(event.decorations, True)
        self.assertEqual(event.parties, True)
        self.assertEqual(event.expected_budget, 1000)

    def test_user_can_search_events(self):
        """
        Test that the user can not search events
        """
        response = self.client.get('/events/event/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search')

    def test_user_can_view_events(self):
        """
        Test that the user can view events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            expected_budget=1000,
        )
        response = self.client.get(f'/events/event/{event.id}/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        self.assertContains(response, 'Test Event')
        self.assertContains(response, '2021-01-01')
        self.assertContains(response, '100')
        self.assertContains(response, '1000')

    def test_user_cannot_delete_events(self):
        """
        Test that the user can not delete events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            meals=True,
            drinks=True,
            expected_budget=1000,
        )
        response = self.client.post(f'/events/event/{event.id}/delete/', {
            'post': 'yes'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 1)

    def test_user_cannot_create_event(self):
        """
        Test that the user can not create an event
        """
        response = self.client.post('/events/event/add/', {
            'record_number': '',
            'client_name': 'Test Client',
            'event_type': 'Test Event',
            'from_date': '2021-01-01',
            'to_date': '2021-01-01',
            'attendes': 100,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 1000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 0)

    def test_user_can_view_event_when_last(self):
        """
        Test that the user can view events when last
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            _status='senior_approval_last',
        )
        response = self.client.get(f'/events/event/{event.id}/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        self.assertContains(response, 'Test Event')

    def test_user_can_change_event_when_last(self):
        """
        Test that the user can change events when last
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            _status='senior_approval_last',
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'record_number': '',
            'client_name': 'Test Client 2',
            'event_type': 'Test Event 2',
            '_status': 'senior_approval_last',
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client 2')
        self.assertEqual(event.event_type, 'Test Event 2')


class FinancialManagerTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        group = create_group('Financial manager', ["change_event", "view_event"])
        self.user.groups.add(group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_permission_to_change_events(self):
        """
        Test that the user has the change_events permission
        """
        self.assertTrue(self.user.has_perm('events.change_event'))

    def test_user_has_not_permission_to_create_events(self):
        """
        Test that the user has not the add_events permission
        """
        self.assertFalse(self.user.has_perm('events.add_event'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that the user has not the delete_events permission
        """
        self.assertFalse(self.user.has_perm('events.delete_event'))
    
    def test_user_has_permission_to_view_events(self):
        """
        Test that the user has the view_events permission
        """
        self.assertTrue(self.user.has_perm('events.view_event'))

    def test_user_can_change_event(self):
        """
        Test that the user can change an event
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
            _status='finance_approval',
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'record_number': '',
            'client_name': 'Test Client 2',
            'event_type': 'Test Event 2',
            'from_date': '2021-01-02',
            'to_date': '2021-01-02',
            'attendes': 200,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 2000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client 2')
        self.assertEqual(event.event_type, 'Test Event 2')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-02')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-02')

    def test_user_cannot_change_event_with_invalid_data(self):
        """
        Test that the user can not change an event with invalid data
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
            _status='finance_approval',
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'client_name': '',
            'event_type': '',
            'from_date': '',
            'to_date': '',
            'attendes': '',
            'decorations': '',
            'meals': '',
            'drinks': '',
            'photos_filming': '',
            'parties': '',
            'expected_budget': '',
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client')
        self.assertEqual(event.event_type, 'Test Event')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.attendes, 100)
        self.assertEqual(event.decorations, True)
        self.assertEqual(event.parties, True)
        self.assertEqual(event.expected_budget, 1000)

    def test_user_can_search_events(self):
        """
        Test that the user can not search events
        """
        response = self.client.get('/events/event/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search')

    def test_user_can_view_events(self):
        """
        Test that the user can view events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            expected_budget=1000,
            _status='finance_approval',
        )
        response = self.client.get(f'/events/event/{event.id}/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        self.assertContains(response, 'Test Event')
        self.assertContains(response, '2021-01-01')
        self.assertContains(response, '100')
        self.assertContains(response, '1000')

    def test_user_cannot_delete_events(self):
        """
        Test that the user can not delete events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            meals=True,
            drinks=True,
            expected_budget=1000,
            _status='finance_approval',
        )
        response = self.client.post(f'/events/event/{event.id}/delete/', {
            'post': 'yes'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 1)

    def test_user_cannot_create_event(self):
        """
        Test that the user can not create an event
        """
        response = self.client.post('/events/event/add/', {
            'record_number': '',
            'client_name': 'Test Client',
            'event_type': 'Test Event',
            'from_date': '2021-01-01',
            'to_date': '2021-01-01',
            'attendes': 100,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 1000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 0)


class AdministrationManagerTestCase(TestCase):
    def setUp(self):
        self.user = create_user()
        group = create_group('Administration manager', ["change_event", "view_event"])
        self.user.groups.add(group)
        self.client.login(username='testuser', password='testpass')

    def test_user_has_permission_to_change_events(self):
        """
        Test that the user has the change_events permission
        """
        self.assertTrue(self.user.has_perm('events.change_event'))

    def test_user_has_not_permission_to_create_events(self):
        """
        Test that the user has not the add_events permission
        """
        self.assertFalse(self.user.has_perm('events.add_event'))

    def test_user_has_not_permission_to_delete_events(self):
        """
        Test that the user has not the delete_events permission
        """
        self.assertFalse(self.user.has_perm('events.delete_event'))
    
    def test_user_has_permission_to_view_events(self):
        """
        Test that the user has the view_events permission
        """
        self.assertTrue(self.user.has_perm('events.view_event'))

    def test_user_can_change_event(self):
        """
        Test that the user can change an event
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
            _status='admin_approval',
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.pk}/change/', {
            'record_number': '',
            'client_name': 'Test Client 2',
            'event_type': 'Test Event 2',
            'from_date': '2021-01-02',
            'to_date': '2021-01-02',
            'attendes': 200,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 2000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client 2')
        self.assertEqual(event.event_type, 'Test Event 2')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-02')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-02')

    def test_user_cannot_change_event_with_invalid_data(self):
        """
        Test that the user can not change an event with invalid data
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            decorations=True,
            parties=True,
            expected_budget=1000,
            _status='admin_approval',
        )
        response: HttpResponse = self.client.post(f'/events/event/{event.id}/change/', {
            'client_name': '',
            'event_type': '',
            'from_date': '',
            'to_date': '',
            'attendes': '',
            'decorations': '',
            'meals': '',
            'drinks': '',
            'photos_filming': '',
            'parties': '',
            'expected_budget': '',
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.client_name, 'Test Client')
        self.assertEqual(event.event_type, 'Test Event')
        self.assertEqual(event.from_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.to_date.strftime('%Y-%m-%d'), '2021-01-01')
        self.assertEqual(event.attendes, 100)
        self.assertEqual(event.decorations, True)
        self.assertEqual(event.parties, True)
        self.assertEqual(event.expected_budget, 1000)

    def test_user_can_search_events(self):
        """
        Test that the user can not search events
        """
        response = self.client.get('/events/event/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search')
    
    def test_user_can_view_events(self):
        """
        Test that the user can view events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            expected_budget=1000,
            _status='admin_approval',
        )
        response = self.client.get(f'/events/event/{event.pk}/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')
        self.assertContains(response, 'Test Event')
        self.assertContains(response, '2021-01-01')
        self.assertContains(response, '100')
        self.assertContains(response, '1000')
    
    def test_user_cannot_delete_events(self):
        """
        Test that the user can not delete events
        """
        event: Event = Event.objects.create(
            client_name='Test Client',
            event_type='Test Event',
            from_date='2021-01-01',
            to_date='2021-01-01',
            attendes=100,
            meals=True,
            drinks=True,
            expected_budget=1000,
            _status='admin_approval',
        )
        response = self.client.post(f'/events/event/{event.id}/delete/', {
            'post': 'yes'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 1)

    def test_user_cannot_create_event(self):
        """
        Test that the user can not create an event
        """
        response = self.client.post('/events/event/add/', {
            'record_number': '',
            'client_name': 'Test Client',
            'event_type': 'Test Event',
            'from_date': '2021-01-01',
            'to_date': '2021-01-01',
            'attendes': 100,
            'meals': 'on',
            'drinks': 'on',
            'expected_budget': 1000,
            '_save': 'Save'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 0)

    