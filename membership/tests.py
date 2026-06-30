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

    def test_upgrade_page_shows_updated_summary_labels_and_values(self):
        UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('membership:upgrade', args=[self.pro_plan.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Starts')
        self.assertContains(response, 'Expires')
        self.assertContains(response, 'Remaining')
        self.assertContains(response, 'Current Plan Credit')
        self.assertContains(response, 'Total Amount Due')
        self.assertEqual(response.context['new_plan_remaining_days'], self.pro_plan.get_duration_days())

    def test_has_active_membership_uses_membership_record_when_flag_is_stale(self):
        user = get_user_model().objects.create_user(
            username='staleflaguser',
            email='stale@example.com',
            password='strongpass123'
        )
        UserMembership.objects.create(
            user=user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        user.membership_active = False
        user.save(update_fields=['membership_active'])

        self.assertTrue(user.has_active_membership())

    def test_plans_page_shows_only_three_canonical_tiers(self):
        MembershipPlan.objects.create(
            name='Basic Plan Duplicate',
            plan_type='basic',
            price=199,
            features=['Workout plans']
        )
        MembershipPlan.objects.create(
            name='Pro Plan Duplicate',
            plan_type='pro',
            price=399,
            features=['Workout plans']
        )
        MembershipPlan.objects.create(
            name='Premium Plan Duplicate',
            plan_type='premium',
            price=599,
            features=['Workout plans']
        )
        MembershipPlan.objects.create(
            name='Extra Basic Plan',
            plan_type='basic',
            price=299,
            features=['Workout plans']
        )

        response = self.client.get(reverse('membership:plans'))

        self.assertEqual(response.status_code, 200)
        plans = response.context['plans']
        self.assertEqual(len(plans), 3)
        self.assertEqual([plan.plan_type for plan in plans], ['basic', 'pro', 'premium'])

    def test_upgrade_page_shows_breakdown_for_zero_amount_upgrades(self):
        free_plan = MembershipPlan.objects.create(
            name='Premium Plan',
            plan_type='premium',
            price=3,
            features=['Workout plans']
        )
        UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('membership:upgrade', args=[free_plan.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Current Plan Credit')
        self.assertContains(response, 'Total Amount Due')

    def test_payments_upgrade_page_shows_summary_values(self):
        UserMembership.objects.create(
            user=self.user,
            plan=self.basic_plan,
            end_date=timezone.now() + timedelta(days=30),
            amount_paid=199,
            status='active'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('payments:upgrade_membership'), {'plan_id': self.pro_plan.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Starts')
        self.assertContains(response, 'Expires')
        self.assertContains(response, 'Current Plan Credit')
        self.assertContains(response, 'Total Amount Due')
