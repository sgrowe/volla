from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status


class RegisterApiTest(APITestCase):

    def test_register(self):
        url = reverse('user-list')
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": "theduuudeman123",
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        self.assertNotIn('password', response.data)

    def test_email_required_to_register(self):
        url = reverse('user-list')
        post_data = {
            "username": "somedude",
            "password": "theduuudeman123",
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_password_required_to_register(self):
        url = reverse('user-list')
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": ""
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')

    def test_user_is_logged_in_after_register(self):
        url = reverse('user-list')
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": "theduuudeman123",
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the user seems to be logged in:
        self.assertIn('_auth_user_id', self.client.session)

    def test_common_passwords_are_rejected(self):
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": "password"
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This password is too common.')

