from unittest.mock import patch
from django.test import TestCase
from django.test import override_settings
from django.core.urlresolvers import reverse
from users.forms import RegisterForm
from users.models import User


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse('register')
        self.post_data = self.get_post_data('BillyBob43', 'billy@yeeehah.com', 'password123')

    def get_post_data(self, username, email, password):
        return {
            'username': username,
            'email': email,
            'password': password,
            'password_repeat': password,
        }

    def test_view_displays_register_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], RegisterForm)

    @patch('users.views.RegisterForm')
    def test_view_uses_register_form(self, form):
        self.client.get(self.url)
        form.assert_called_once_with()

    @patch.object(RegisterForm, 'is_valid')
    def test_view_uses_register_form_on_post(self, is_valid):
        data = self.get_post_data('billy_bob_beats', 'billybob@yahoo.com',  'guns4lief')
        self.client.post(self.url, data)
        is_valid.assert_called_once_with()

    def test_submit_url_is_register_url(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'action="{}"'.format(self.url))

    def test_creates_new_user_on_register(self):
        username = 'BillyBob43'
        email = 'billy@yeeehah.com'
        password = 'password123'
        data = self.get_post_data(username, email, password)
        self.client.post(self.url, data)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_is_logged_in_after_register(self):
        self.client.post(self.url, self.post_data)
        user = User.objects.get()
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_redirected_to_home_page_after_register(self):
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, reverse('home'))
