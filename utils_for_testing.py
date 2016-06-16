from django.test import TestCase
import http_status_codes as status
from users.models import User
from vollumes.models import create_validate_and_save_vollume
from random import randint


# TODO: Investigate a better way of using random numbers in unit tests (for repeatability)
def get_random_int():
    return randint(1, 100000)


def test_server_url(item):
    return 'http://testserver' + item.get_absolute_url()


def create_and_save_dummy_user(**kwargs):
    kwargs.setdefault('username', 'some_user')
    kwargs.setdefault('email', '{}@gmail.com'.format(kwargs['username']))
    password = kwargs.pop('password', 'password123')
    user = User(**kwargs)
    user.set_password(password)
    user.save()
    return user


def create_and_save_dummy_vollume(**kwargs):
    if 'author' not in kwargs:
        kwargs['author'] = create_and_save_dummy_user()
    kwargs.setdefault('title', "You won't believe what she said next!")
    kwargs.setdefault('text', 'Some words and words and words...')
    return create_validate_and_save_vollume(**kwargs)


class WebTestCase(TestCase):
    url = ''
    post_data = {}

    def post_request(self, url=None, data=None, status=status.HTTP_302_FOUND):
        url = url or self.url
        data = data or self.post_data
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status)
        return response

    def get_request(self, url=None, status=status.HTTP_200_OK):
        url = url or self.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)
        return response
