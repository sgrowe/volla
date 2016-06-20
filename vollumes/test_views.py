from django.core.exceptions import ValidationError
from utils_for_testing import WebTestCase, create_and_save_dummy_vollume, create_and_save_dummy_user
from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
import http_status_codes as status
from django.core.urlresolvers import reverse
from vollumes.models import Vollume, VollumeChunk
from vollumes.views import handle_new_paragraph_form, vollume_page, NewParagraphForm, CreateVollumeForm


class HomePageTests(WebTestCase):
    def setUp(self):
        self.url = reverse('home')

    def test_includes_login_link_when_logged_out(self):
        response = self.get_request()
        login_link = '<a href="{}?next={}">Login</a>'.format(reverse('login'), self.url)
        self.assertContains(response, login_link, html=True)

    def test_includes_logout_link_when_logged_in(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        response = self.get_request()
        logout_link = '<a href="{}?next={}">Logout</a>'.format(reverse('logout'), self.url)
        self.assertContains(response, logout_link, html=True)


class WelcomePageTests(TestCase):
    def test_returns_valid(self):
        url = reverse('welcome-tour')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateVollumeViewTests(WebTestCase):
    def setUp(self):
        self.url = reverse('new-vollume')
        self.post_data = {
            'title': "Check it out bruh",
            'text': 'Here are a load of words...',
        }

    def test_must_be_logged_in_to_create_new_vollume(self):
        login_url = '{}?next={}'.format(reverse('login'), self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, login_url)
        response = self.client.post(self.url, self.post_data)
        self.assertRedirects(response, login_url)

    def test_redirects_to_created_vollume_on_success(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        response = self.post_request()
        self.assertEqual(Vollume.objects.count(), 1)
        vollume = Vollume.objects.first()
        self.assertRedirects(response, vollume.get_absolute_url(), fetch_redirect_response=False)

    def test_author_of_created_vollume_and_paragraph_is_logged_in_user(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        self.post_request()
        self.assertEqual(Vollume.objects.count(), 1)
        self.assertEqual(VollumeChunk.objects.count(), 1)
        vollume = Vollume.objects.first()
        self.assertEqual(vollume.author, user)
        self.assertEqual(vollume.first_paragraph.author, user)

    @patch('vollumes.views.show_validation_errors_in_form')
    def test_uses_show_validation_errors_in_form(self, show_validation_errors_mock):
        self.client.force_login(create_and_save_dummy_user())
        self.post_data['title'] += 'a' * 200
        with self.assertRaises(ValidationError):
            self.post_request()
        self.assertEqual(show_validation_errors_mock.call_count, 1)
        self.assertIsInstance(show_validation_errors_mock.call_args[0][0], CreateVollumeForm)


class VollumeStartPageTests(WebTestCase):
    def test_view_uses_correct_vollume(self):
        vollume = create_and_save_dummy_vollume()
        response = self.get_request(vollume.get_absolute_url())
        self.assertIn('paragraphs', response.context)
        self.assertEqual(response.context['paragraphs'][0].pk, vollume.first_paragraph.pk)

    def test_contains_first_paragraph_text(self):
        vollume = create_and_save_dummy_vollume()
        response = self.get_request(vollume.get_absolute_url())
        self.assertContains(response, '{}'.format(vollume.first_paragraph.text))

    def test_contains_link_to_next_page(self):
        vollume = create_and_save_dummy_vollume()
        second_para = vollume.first_paragraph.add_child(
            vollume.author,
            'Even more words'
        )
        url = 'href="{}"'.format(second_para.get_absolute_url())
        response = self.get_request(vollume.get_absolute_url())
        self.assertContains(response, url)


class HandleNewParagraphFormTests(TestCase):
    def setUp(self):
        self.requests = RequestFactory()

    def test_redirects_anonymous_users_to_login_on_post(self):
        request = self.requests.post('/')
        request.user = AnonymousUser()
        parent_paragraph = create_and_save_dummy_vollume().first_paragraph
        result = handle_new_paragraph_form(request, parent_paragraph)
        self.assertIsInstance(result, HttpResponseRedirect)

    @patch('vollumes.views.show_validation_errors_in_form')
    def test_returned_form_has_validation_errors_on_invalid_post(self, show_validation_errors_mock):
        request = self.requests.post('/wiki/Chickasaw_Turnpike', {'text': 'Too many words ' + ('a' * 500)})
        request.user = create_and_save_dummy_user()
        parent_paragraph = create_and_save_dummy_vollume(author=request.user).first_paragraph
        with self.assertRaises(ValidationError):
            handle_new_paragraph_form(request, parent_paragraph)
        self.assertEqual(show_validation_errors_mock.call_count, 1)
        self.assertIsInstance(show_validation_errors_mock.call_args[0][0], NewParagraphForm)


class VollumePageTests(WebTestCase):

    class TestException(Exception):
        pass

    @patch('vollumes.views.get_paragraph_or_404', side_effect=TestException)
    def test_fetch_vollume_and_paragraph_by_hashid(self, get_parent_paragraph):
        vollume_hashid = '4fj'
        parent_paragraph_hashid = 'fjgh40'
        url = reverse('vollume-page', kwargs={'vollume_id': vollume_hashid, 'paragraph_id': parent_paragraph_hashid})
        with self.assertRaises(self.TestException):
            self.get_request(url)
        get_parent_paragraph.assert_called_once_with(vollume_hashid, parent_paragraph_hashid)

    def test_shows_the_right_paragraphs(self):
        vollume = create_and_save_dummy_vollume()
        second_user = create_and_save_dummy_user(username='Wendy')
        para_a = vollume.first_paragraph.add_child(
            author=vollume.author,
            text='Add on some extra words.'
        )
        para_b = vollume.first_paragraph.add_child(
            author=second_user,
            text="I'll add in a bit of extra stuff too!"
        )
        self.assertEqual(para_a.get_absolute_url(), para_b.get_absolute_url())
        response = self.get_request(para_a.get_absolute_url())
        paragraphs = response.context['paragraphs']
        self.assertEqual(len(paragraphs), 2)
        self.assertIn(para_a, paragraphs)
        self.assertIn(para_b, paragraphs)

    def test_contains_links_to_child_pages(self):
        vollume = create_and_save_dummy_vollume()
        second_user = create_and_save_dummy_user(username='Wendy')
        second_page_para_a = vollume.first_paragraph.add_child(
            author=second_user,
            text='Add on some extra words.'
        )
        second_page_para_b = vollume.first_paragraph.add_child(
            author=vollume.author,
            text='Enough with all this writing'
        )
        third_page_para = second_page_para_a.add_child(
            author=second_user,
            text="I'll add in a bit of extra stuff too!"
        )
        response = self.get_request(second_page_para_a.get_absolute_url())
        self.assertContains(response, vollume.first_paragraph.get_absolute_url())
        self.assertContains(response, second_page_para_a.get_next_page_url())
        self.assertContains(response, second_page_para_b.get_next_page_url())

    def test_form_posts_to_same_page(self):
        vollume = create_and_save_dummy_vollume()
        second_user = create_and_save_dummy_user(username='Wendy')
        self.client.force_login(second_user)
        second_paragraph = vollume.first_paragraph.add_child(
            author=second_user,
            text='Add on some extra words.'
        )
        url = second_paragraph.get_absolute_url()
        response = self.get_request(url)
        self.assertContains(response, 'action="{}"'.format(url))

    def test_returns_redirects_returned_by_handle_new_paragraph_form(self):
        vollume = create_and_save_dummy_vollume()
        redirect = HttpResponseRedirect('/')
        request = RequestFactory().get('/new-paragraph/')
        with patch('vollumes.views.handle_new_paragraph_form', return_value=redirect):
            response = vollume_page(request, vollume.hashid, vollume.first_paragraph.hashid)
            self.assertIs(response, redirect)

    def test_displays_form_returned_by_handle_new_paragraph(self):
        vollume = create_and_save_dummy_vollume()
        form = Mock(spec=NewParagraphForm)
        url_kwargs = {'vollume_id': vollume.hashid, 'paragraph_id': vollume.first_paragraph.hashid}
        url = reverse('vollume-page', kwargs=url_kwargs)
        with patch('vollumes.views.handle_new_paragraph_form', return_value=form):
            response = self.get_request(url)
            self.assertIs(response.context['form'], form)


class TestUserProfilePage(WebTestCase):
    pass
