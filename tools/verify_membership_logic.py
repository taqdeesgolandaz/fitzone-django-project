import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitzone.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from membership.models import MembershipPlan, UserMembership
from datetime import timedelta

user = get_user_model().objects.filter(username='verifyuser').first()
if user is None:
    user = get_user_model().objects.create_user(username='verifyuser', email='verify@example.com', password='pass1234')

basic = MembershipPlan.objects.filter(plan_type='basic').first()
pro = MembershipPlan.objects.filter(plan_type='pro').first()
if not basic:
    basic = MembershipPlan.objects.create(name='Basic Plan', plan_type='basic', price=199, features=['Workout plans'])
if not pro:
    pro = MembershipPlan.objects.create(name='Pro Plan', plan_type='pro', price=399, features=['Workout plans', 'Diet plans'])

old = UserMembership.objects.create(user=user, plan=basic, end_date=timezone.now() + timedelta(days=30), amount_paid=199, status='active')
print('before', UserMembership.objects.filter(user=user, status='active').count())
UserMembership.deactivate_other_active_memberships(user, keep_membership_id=old.id)
print('after', UserMembership.objects.filter(user=user, status='active').count())
print('old_status', old.status)
