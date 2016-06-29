from django.test import TestCase
from users.forms import RegisterForm
from utils_for_testing import create_and_save_dummy_user


def disable_logging_when_testing():
    import logging
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        logging.disable(logging.CRITICAL)


disable_logging_when_testing()


class RegisterFormTests(TestCase):
    def test_two_password_fields_must_match(self):
        form_data = {
            'username': 'Benny',
            'email': 'berty@gmail.com',
            'password': 'password123',
            'password_repeat': 'nottherightpassword',
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password_repeat', form.errors)

    def test_required_fields(self):
        required_fields = ('username', 'email', 'password', 'password_repeat')
        for field in required_fields:
            form_data = {
                'username': 'Berty',
                'email': 'berty@gmail.com',
                'password': 'password123',
                'password_repeat': 'password123',
            }
            del form_data[field]
            form = RegisterForm(form_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_validates_password(self):
        for password in ('password', 'abc123'):
            form_data = {
                'username': 'Berty',
                'email': 'berty@gmail.com',
                'password': password,
                'password_repeat': password,
            }
            form = RegisterForm(form_data)
            self.assertFalse(form.is_valid(), "Form accepted password: {}".format(password))
            self.assertIn('password', form.errors)

    def test_cannot_register_with_duplicate_usernames(self):
        username = 'BillyBob43'
        create_and_save_dummy_user(username=username, email='billy@yeeehah.com')
        form_data = {
            'username': username,
            'email': 'some_other_billy@gmail.com',
            'password': 'billybeatsall',
            'password_repeat': 'billybeatsall',
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('username'))

    def test_cannot_register_with_duplicate_emails(self):
        email = 'billy@yeeehah.com'
        create_and_save_dummy_user(username='BillyBob43', email=email)
        form_data = {
            'username': 'Bobbo',
            'email': email,
            'password': 'password123',
            'password_repeat': 'password123',
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email'))
