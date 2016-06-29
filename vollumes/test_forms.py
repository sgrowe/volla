from django.test import TestCase, RequestFactory
from unittest.mock import patch
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from utils_for_testing import create_and_save_dummy_vollume
from vollumes.forms import handle_new_paragraph_form, NewParagraphForm
from vollumes.models import VollumeChunk


class HandleNewParagraphFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vollume = create_and_save_dummy_vollume()

    def setUp(self):
        self.requests = RequestFactory()

    def test_redirects_anonymous_users_to_login_on_post(self):
        request = self.requests.post('/')
        request.user = AnonymousUser()
        parent_paragraph = self.vollume.first_paragraph
        result = handle_new_paragraph_form(request, parent_paragraph)
        self.assertIsInstance(result, HttpResponseRedirect)

    @patch('vollumes.forms.show_validation_errors_in_form')
    def test_returned_form_has_validation_errors_on_invalid_post(self, show_validation_errors_mock):
        request = self.requests.post('/wiki/Chickasaw_Turnpike', {'text': 'Too many words ' + ('a' * 500)})
        request.user = self.vollume.author
        parent_paragraph = self.vollume.first_paragraph
        with self.assertRaises(ValidationError):
            handle_new_paragraph_form(request, parent_paragraph)
        self.assertEqual(show_validation_errors_mock.call_count, 1)
        self.assertIsInstance(show_validation_errors_mock.call_args[0][0], NewParagraphForm)

    def test_creates_new_paragraph_on_valid_post(self):
        post_data = {
            'title': 'Fly you fools',
            'text': "Why didn't the eagles just fly them there?",
        }
        request = self.requests.post('/wiki/Chickasaw_Turnpike', post_data)
        request.user = self.vollume.author
        parent_paragraph = self.vollume.first_paragraph
        self.assertEqual(VollumeChunk.objects.count(), 1)
        response = handle_new_paragraph_form(request, parent_paragraph)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(VollumeChunk.objects.count(), 2)
        self.assertEqual(parent_paragraph.children.count(), 1)
