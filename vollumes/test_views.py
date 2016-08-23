from utils_for_testing import WebTestCase, create_and_save_dummy_vollume, create_and_save_dummy_user
from unittest.mock import Mock, patch
from django.test import RequestFactory
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from vollumes.models import Vollume, VollumeChunk
from vollumes.forms import NewParagraphForm, CreateVollumeForm
from vollumes.views import vollume_page


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


class WelcomePageTests(WebTestCase):
    def setUp(self):
        self.url = reverse('welcome-tour')

    def test_contains_register_link_if_user_logged_out(self):
        response = self.get_request()
        self.assertContains(response, reverse('register'))


class CreateVollumeViewTests(WebTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_and_save_dummy_user()

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
        self.client.force_login(self.user)
        response = self.post_request()
        self.assertEqual(Vollume.objects.count(), 1)
        vollume = Vollume.objects.first()
        self.assertRedirects(response, vollume.get_absolute_url(), fetch_redirect_response=False)

    def test_author_of_created_vollume_and_paragraph_is_logged_in_user(self):
        self.client.force_login(self.user)
        self.post_request()
        self.assertEqual(Vollume.objects.count(), 1)
        self.assertEqual(VollumeChunk.objects.count(), 1)
        vollume = Vollume.objects.first()
        self.assertEqual(vollume.author, self.user)
        self.assertEqual(vollume.first_paragraph.author, self.user)

    @patch('vollumes.views.show_validation_errors_in_form')
    def test_uses_show_validation_errors_in_form(self, show_validation_errors_mock):
        self.client.force_login(self.user)
        self.post_data['title'] += 'a' * 200
        with self.assertRaises(ValidationError):
            self.post_request()
        self.assertEqual(show_validation_errors_mock.call_count, 1)
        self.assertIsInstance(show_validation_errors_mock.call_args[0][0], CreateVollumeForm)


class RegisterThenCreateVollumeTests(WebTestCase):
    def test_user_can_register_and_then_create_new_vollume(self):
        register_url = reverse('register')
        register_data = {
            'username': 'JimmyJoo',
            'email': 'jj@gmail.com',
            'password': 'flujjer1',
            'password_repeat': 'flujjer1',
        }
        self.post_request(register_url, register_data)
        new_vollume_url = reverse('new-vollume')
        vollume_data = {
            'title': 'Within reach',
            'text': 'What does it even mean, dude?'
        }
        self.post_request(new_vollume_url, vollume_data)


class VollumeStartPageTests(WebTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vollume = create_and_save_dummy_vollume()

    def setUp(self):
        self.url = self.vollume.get_absolute_url()

    def test_view_uses_correct_vollume(self):
        response = self.get_request()
        self.assertIn('paragraphs', response.context)
        self.assertEqual(response.context['paragraphs'][0].pk, self.vollume.first_paragraph.pk)

    def test_contains_first_paragraph_text(self):
        response = self.get_request()
        self.assertContains(response, self.vollume.first_paragraph.text)

    def test_contains_link_to_next_page(self):
        second_para = self.vollume.first_paragraph.add_child(
            self.vollume.author,
            'Even more words'
        )
        url = 'href="{}"'.format(second_para.get_absolute_url())
        response = self.get_request()
        self.assertContains(response, url)


class VollumePageTests(WebTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vollume = create_and_save_dummy_vollume()
        cls.second_user = create_and_save_dummy_user(username='Wendy')

    def test_fetch_vollume_and_paragraph_by_hashid(self):
        vollume_hashid = '4fj'
        parent_para_hashid = 'fjgh40'

        class TestException(Exception):
            pass

        with patch('vollumes.views.get_paragraph_or_404', side_effect=TestException) as get_parent_paragraph:
            url = reverse('vollume-page', kwargs={'vollume_id': vollume_hashid, 'paragraph_id': parent_para_hashid})
            with self.assertRaises(TestException):
                self.get_request(url)
        get_parent_paragraph.assert_called_once_with(vollume_hashid, parent_para_hashid)

    def test_shows_the_right_paragraphs(self):
        para_a = self.vollume.first_paragraph.add_child(
            author=self.vollume.author,
            text='Add on some extra words.'
        )
        para_b = self.vollume.first_paragraph.add_child(
            author=self.second_user,
            text="I'll add in a bit of extra stuff too!"
        )
        self.assertEqual(para_a.get_absolute_url(), para_b.get_absolute_url())
        response = self.get_request(para_a.get_absolute_url())
        paragraphs = response.context['paragraphs']
        self.assertEqual(len(paragraphs), 2)
        self.assertIn(para_a, paragraphs)
        self.assertIn(para_b, paragraphs)

    def test_contains_links_to_child_pages(self):
        second_page_para_a = self.vollume.first_paragraph.add_child(
            author=self.second_user,
            text='Add on some extra words.'
        )
        second_page_para_b = self.vollume.first_paragraph.add_child(
            author=self.vollume.author,
            text='Enough with all this writing'
        )
        third_page_para = second_page_para_a.add_child(
            author=self.second_user,
            text="I'll add in a bit of extra stuff too!"
        )
        response = self.get_request(second_page_para_a.get_absolute_url())
        self.assertContains(response, self.vollume.first_paragraph.get_absolute_url())
        self.assertContains(response, second_page_para_a.get_next_page_url())
        self.assertContains(response, second_page_para_b.get_next_page_url())

    def test_form_posts_to_same_page(self):
        self.client.force_login(self.second_user)
        second_paragraph = self.vollume.first_paragraph.add_child(
            author=self.second_user,
            text='Add on some extra words.'
        )
        url = second_paragraph.get_absolute_url()
        response = self.get_request(url)
        self.assertContains(response, 'action="{}"'.format(url))

    def test_returns_redirects_returned_by_handle_new_paragraph_form(self):
        redirect = HttpResponseRedirect('/')
        request = RequestFactory().get('/new-paragraph/')
        with patch('vollumes.views.handle_new_paragraph_form', return_value=redirect):
            response = vollume_page(request, self.vollume.hashid, self.vollume.first_paragraph.hashid)
            self.assertIs(response, redirect)

    def test_displays_form_returned_by_handle_new_paragraph(self):
        form = Mock(spec=NewParagraphForm)
        url_kwargs = {'vollume_id': self.vollume.hashid, 'paragraph_id': self.vollume.first_paragraph.hashid}
        url = reverse('vollume-page', kwargs=url_kwargs)
        with patch('vollumes.views.handle_new_paragraph_form', return_value=form):
            response = self.get_request(url)
            self.assertIs(response.context['form'], form)


class TestUserProfilePage(WebTestCase):
    pass
