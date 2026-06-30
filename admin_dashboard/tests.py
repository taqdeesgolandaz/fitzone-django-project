from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from membership.models import MembershipPlan, UserMembership


class MembershipReportTests(TestCase):
    def test_membership_report_excludes_debug_and_test_accounts(self):
        staff_user = get_user_model().objects.create_user(
            username='adminstaff',
            email='adminstaff@example.com',
            password='strongpass123',
            is_staff=True,
            is_superuser=False,
        )
        plan = MembershipPlan.objects.create(
            name='Basic Plan',
            plan_type='basic',
            price=199,
            features=['Workout plans']
        )

        real_user = get_user_model().objects.create_user(
            username='taqdeesgolandaz',
            email='taqdees@example.com',
            password='strongpass123'
        )
        debug_user = get_user_model().objects.create_user(
            username='debuguser1',
            email='debuguser1@example.com',
            password='strongpass123'
        )
        verify_user = get_user_model().objects.create_user(
            username='verifyuser',
            email='verify@example.com',
            password='strongpass123'
        )

        UserMembership.objects.create(
            user=real_user,
            plan=plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )
        UserMembership.objects.create(
            user=debug_user,
            plan=plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )
        UserMembership.objects.create(
            user=verify_user,
            plan=plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        self.client.force_login(staff_user)
        response = self.client.get(reverse('admin_dashboard:membership_report'))

        self.assertEqual(response.status_code, 200)
        displayed_users = [membership.user.username for membership in response.context['memberships']]
        self.assertIn('taqdeesgolandaz', displayed_users)
        self.assertNotIn('debuguser1', displayed_users)
        self.assertNotIn('verifyuser', displayed_users)
