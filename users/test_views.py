from unittest.mock import patch
from utils_for_testing import WebTestCase
from django.test import override_settings
from django.core.urlresolvers import reverse
from users.forms import RegisterForm
from users.models import User


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class RegisterViewTests(WebTestCase):
    def setUp(self):
        self.url = reverse('register')
        self.set_post_data('BillyBob43', 'billy@yeeehah.com', 'password123')

    def set_post_data(self, username, email, password):
        self.post_data = {
            'username': username,
            'email': email,
            'password': password,
            'password_repeat': password,
        }

    def test_view_displays_register_form(self):
        response = self.get_request()
        self.assertIsInstance(response.context['form'], RegisterForm)

    @patch('users.views.RegisterForm')
    def test_view_uses_register_form(self, form):
        self.get_request()
        form.assert_called_once_with()

    @patch('users.views.RegisterForm.is_valid')
    def test_view_uses_register_form_on_post(self, is_valid):
        self.set_post_data('billy_bob_beats', 'billybob@yahoo.com',  'guns4lief')
        self.post_request()
        is_valid.assert_called_once_with()

    def test_submit_url_is_register_url(self):
        response = self.get_request()
        self.assertContains(response, 'action="{}"'.format(self.url))

    def test_creates_new_user_on_register(self):
        username = 'BillyBob43'
        email = 'billy@yeeehah.com'
        password = 'password123'
        self.set_post_data(username, email, password)
        self.post_request()
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_is_logged_in_after_register(self):
        self.post_request()
        user = User.objects.get()
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_redirected_to_home_page_after_register(self):
        response = self.post_request()
        self.assertRedirects(response, reverse('home'))
