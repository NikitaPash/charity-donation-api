"""
Tests for User model and manager.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user(email='testemail@example.com', password='testpassword123'):
    """Helper function to create and return a test user."""
    return get_user_model().objects.create_user(email, password)


class UserModelTests(TestCase):
    """Test User model."""

    def setUp(self):
        """Set up test dependencies."""
        self.email = 'testemail@example.com'
        self.password = 'testpassword123'

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        user = create_user()

        self.assertEqual(user.email, self.email)
        self.assertTrue(user.check_password, self.password)

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = create_user(email=email)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            create_user(email='')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            self.email,
            self.password,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_default_role_assigned_correctly(self):
        """Test assigment of a default role."""
        user = create_user()

        self.assertEqual(user.get_role_display(), 'Donor')

    def test_role_assigned_correctly(self):
        """Test assigning a role."""
        user = create_user()
        role_to_assign = 'CM'
        user.role = role_to_assign

        self.assertEqual(user.role, role_to_assign)
        self.assertEqual(user.get_role_display(), 'Campaign Manager')

    def test_add_balance(self):
        """Test adding to balance."""
        user = create_user(email='testadd1@example.com')
        amount_to_add1 = 55.50
        amount_to_add2 = -10.50
        user.add_balance(amount_to_add1)

        self.assertEqual(user.balance, amount_to_add1)
        with self.assertRaises(ValueError):
            user.add_balance(amount_to_add2)

    def test_deduct_balance(self):
        """Test deducting from balance."""
        user = create_user(email='testdeduct1@example.com')
        balance = user.balance = 100
        amount_to_deduct1 = 55.50
        amount_to_deduct2 = -10.50
        user.deduct_balance(amount_to_deduct1)

        self.assertEqual(user.balance, balance - amount_to_deduct1)
        with self.assertRaises(ValueError):
            user.deduct_balance(amount_to_deduct1)
        with self.assertRaises(ValueError):
            user.deduct_balance(amount_to_deduct2)
