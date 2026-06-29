from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import MembershipPlan, UserMembership


class MembershipLogicTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='memberuser',
            email='member@example.com',
            password='strongpass123'
        )
        self.basic_plan = MembershipPlan.objects.create(
            name='Basic Plan',
            plan_type='basic',
            price=199,
            features=['Workout plans']
        )
        self.pro_plan = MembershipPlan.objects.create(
            name='Pro Plan',
            plan_type='pro',
            price=399,
            features=['Workout plans', 'Diet plans']
        )

    def test_deactivate_previous_active_memberships_on_upgrade(self):
        old_membership = UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        UserMembership.deactivate_other_active_memberships(self.user)
        old_membership.refresh_from_db()

        self.assertEqual(old_membership.status, 'cancelled')
        self.assertFalse(old_membership.is_active())

    def test_my_membership_view_does_not_show_cancelled_membership_as_active(self):
        UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='cancelled'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('membership:my_membership'))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['active_membership'])
        self.assertContains(response, 'No Active Membership')

    def test_upgrade_starts_new_membership_from_upgrade_date(self):
        UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('membership:upgrade', args=[self.pro_plan.id]))

        self.assertEqual(response.status_code, 302)
        new_membership = UserMembership.objects.filter(user=self.user, plan=self.pro_plan, status='active').latest('created_at')
        self.assertTrue(new_membership.start_date <= timezone.now())
        self.assertLessEqual(abs((new_membership.end_date - new_membership.start_date).days - self.pro_plan.get_duration_days()), 1)
