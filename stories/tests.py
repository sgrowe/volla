from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from .fields import HashidAutoField


class HashidFieldTest(SimpleTestCase):
    def test_to_db_value(self):
        field = HashidAutoField()
        self.assertEqual(field.get_prep_value('oj'), 6)


class VollumeApiTest(APITestCase):

    def test_vollumes_list(self):
        url = reverse('vollume-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
