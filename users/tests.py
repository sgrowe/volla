from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from users.models import User


class RegisterTest(APITestCase):

    def test_register(self):
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": "theduuudeman123",
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)
        self.assertIn('id', response.data)
        self.assertNotIn('password', response.data)

    def test_email_required_to_register(self):
        post_data = {
            "username": "somedude",
            "password": "theduuudeman123",
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_password_required_to_register(self):
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": ""
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')

    def test_user_is_logged_in_after_registration(self):
        post_data = {
            "username": "somedude",
            "email": "dude@dude.com",
            "password": "theduuudeman123",
        }
        response = self.client.post(reverse('user-list'), post_data, format='json')
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


class LogoutTest(APITestCase):
    def test_logout(self):
        user = User(username="not for long", email="lskgjn@email.com")
        user.save()
        self.client.force_login(user)
        # Check that the user seems to be logged in:
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('user-logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the user seems to be logged out:
        self.assertNotIn('_auth_user_id', self.client.session)


class LoginTest(APITestCase):
    def test_login(self):
        username = "yo@thebro"
        password = "never gonna guess it"
        user = User(username=username, email="lskgjn@email.com")
        user.set_password(password)
        user.save()
        post_data = {
            'username': username,
            'password': password
        }
        response = self.client.post(reverse('user-login'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_attempt_fail_with_wrong_password(self):
        username = "yo@thebro"
        password = "never gonna guess it"
        user = User(username=username, email="lskgjn@email.com")
        user.set_password(password)
        user.save()
        post_data = {
            'username': username,
            'password': "this aint right"
        }
        response = self.client.post(reverse('user-login'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'][0], 'Incorrect username or password.')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_attempt_fails_with_no_password(self):
        username = "yo@thebro"
        password = "never gonna guess it"
        user = User(username=username, email="lskgjn@email.com")
        user.set_password(password)
        user.save()
        post_data = {
            'username': username
        }
        response = self.client.post(reverse('user-login'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')
        self.assertNotIn('_auth_user_id', self.client.session)
        post_data = {
            'username': username,
            'password': ''
        }
        response = self.client.post(reverse('user-login'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')
        self.assertNotIn('_auth_user_id', self.client.session)


class GetCurrentUserTest(APITestCase):
    def test_user_is_logged_out(self):
        response = self.client.get(reverse('user-logged-in'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.data
        self.assertEqual(len(json['results']), 0)

    def test_user_is_logged_in(self):
        username = "yo@thebro"
        email = "lskgjn@email.com"
        password = "never gonna guess it"
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        self.client.force_login(user)
        response = self.client.get(reverse('user-logged-in'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['results'][0]
        self.assertEqual(user_data['username'], username)
        self.assertEqual(user_data['email'], email)
        self.assertIn('id', user_data)
        self.assertNotIn('password', user_data)

