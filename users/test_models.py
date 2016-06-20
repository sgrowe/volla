from django.test import TestCase
from users.models import User
from django.core import mail
import http_status_codes as status


class UserTests(TestCase):
    def test_get_absolute_url_method(self):
        user = User(username='Mohammed', email='mr-m@yahoo.com')
        user.save()
        response = self.client.get(user.get_absolute_url())
        self.assertTrue(status.is_success(response.status_code))

    def test_email_user(self):
        user = User(username='Missy Elliot', email='missy@gmail.com')
        user.save()
        self.assertEqual(len(mail.outbox), 0)
        user.email_user('Yo', 'Keep it real girl')
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['missy@gmail.com'])
