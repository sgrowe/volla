from unittest import TestCase
from unittest.mock import patch
from django.test import RequestFactory
from urllib.parse import urlparse
from users.helpers import url_for_auth_view_which_returns_to_here


class UrlForAuthViewTests(TestCase):
    def setUp(self):
        self.requests = RequestFactory()

    def test_returns_reversed_url(self):
        for url_name in ('login', 'register', 'logout'):
            request = self.requests.get('/')
            with patch('users.helpers.reverse', return_value='/some-page/') as reverse_mock:
                url = url_for_auth_view_which_returns_to_here(url_name, request)
                path = urlparse(url)[2]
                self.assertEqual(path, '/some-page/')
                reverse_mock.assert_called_once_with(url_name)

    def test_redirect_has_appropriate_query_param(self):
        for current_url in ('/some-where', '/about/us/'):
            request = self.requests.get(current_url)
            url = url_for_auth_view_which_returns_to_here('login', request)
            query_params = urlparse(url)[4]
            self.assertEqual(query_params, 'next={}'.format(current_url))




