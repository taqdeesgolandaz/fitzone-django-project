import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from membership.models import MembershipPlan, UserMembership
from .models import Payment


class MembershipPaymentTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='testuser', password='pass')
		self.client = Client()
		self.client.login(username='testuser', password='pass')

		# Create a membership plan
		self.plan = MembershipPlan.objects.create(
			name='Pro Plan',
			plan_type='pro',
			duration='monthly',
			price=100.00,
			features=[]
		)

		# Create a pending payment for this plan
		self.payment = Payment.objects.create(
			user=self.user,
			amount=self.plan.price,
			razorpay_order_id='order_test_123',
			status='pending',
			transaction_id=f'MEM{self.plan.id}_TEST'
		)

	@patch('payments.views.get_razorpay_client')
	def test_payment_success_activates_membership(self, mock_get_razorpay_client):
		# Mock Razorpay client and signature verification to not raise
		mock_client = mock_get_razorpay_client.return_value
		mock_client.utility.verify_payment_signature.return_value = None

		url = reverse('payments:payment_success')
		payload = {
			'razorpay_payment_id': 'pay_ABC123',
			'razorpay_order_id': 'order_test_123',
			'razorpay_signature': 'sig_TEST'
		}

		response = self.client.post(url, json.dumps(payload), content_type='application/json')
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data.get('success'))

		# Payment updated
		self.payment.refresh_from_db()
		self.assertEqual(self.payment.status, 'success')

		# User membership flags set and UserMembership created
		user = get_user_model().objects.get(pk=self.user.pk)
		self.assertTrue(user.membership_active)
		um = UserMembership.objects.filter(user=user, plan=self.plan).first()
		self.assertIsNotNone(um)

	@patch('payments.views.get_razorpay_client')
	def test_payment_success_accepts_form_encoded_data(self, mock_get_razorpay_client):
		mock_client = mock_get_razorpay_client.return_value
		mock_client.utility.verify_payment_signature.return_value = None

		url = reverse('payments:payment_success')
		response = self.client.post(url, {
			'razorpay_payment_id': 'pay_ABC123',
			'razorpay_order_id': 'order_test_123',
			'razorpay_signature': 'sig_TEST'
		})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

