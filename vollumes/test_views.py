from utils_for_testing import WebTestCase, create_and_save_dummy_vollume, create_and_save_dummy_user
from unittest.mock import patch
import http_status_codes as status
from django.core.urlresolvers import reverse
from vollumes.models import Vollume, VollumeChunk


class HomePageTests(WebTestCase):
    def setUp(self):
        self.url = reverse('home')

    def test_includes_login_link_when_logged_out(self):
        response = self.get_request()
        login_link = '<a href="{}">Login</a>'.format(reverse('login'))
        self.assertContains(response, login_link, html=True)

    def test_includes_logout_link_when_logged_in(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        response = self.get_request()
        logout_link = '<a href="{}">Logout</a>'.format(reverse('logout'))
        self.assertContains(response, logout_link, html=True)


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

    def test_title_validation_errors_are_added_to_form(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        self.post_data['title'] += "a" * Vollume._meta.get_field('title').max_length
        response = self.post_request(status=status.HTTP_200_OK)
        form = response.context['form']
        self.assertTrue(form.has_error('title'))

    def test_text_validation_errors_are_added_to_form(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        self.post_data['text'] += 'a' * 500
        response = self.post_request(status=status.HTTP_200_OK)
        form = response.context['form']
        self.assertTrue(form.has_error('text'))

    def test_vollume_is_not_saved_if_paragraph_invalid(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        del self.post_data['text']
        self.post_request(status=status.HTTP_200_OK)
        self.assertEqual(Vollume.objects.count(), 0)


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


class TestException(Exception):
    pass


class VollumePageTests(WebTestCase):
    @patch('vollumes.views.get_paragraph_or_404', side_effect=TestException)
    def test_fetch_vollume_and_paragraph_by_hashid(self, get_parent_paragraph):
        vollume_hashid = '4fj'
        parent_hashid = 'fjgh40'
        url = reverse('vollume-page', kwargs={'hashid': vollume_hashid, 'page': parent_hashid})
        with self.assertRaises(TestException):
            self.get_request(url)
        get_parent_paragraph.assert_called_once_with(vollume_hashid, parent_hashid)

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
        para_a = vollume.first_paragraph.add_child(
            author=second_user,
            text='Add on some extra words.'
        )
        para_b = vollume.first_paragraph.add_child(
            author=vollume.author,
            text='Enough with all this writing'
        )
        next_page_para = para_a.add_child(
            author=second_user,
            text="I'll add in a bit of extra stuff too!"
        )
        response = self.get_request(para_a.get_absolute_url())
        self.assertContains(response, vollume.first_paragraph.get_absolute_url())
        self.assertContains(response, para_a.get_next_page_url())
        self.assertContains(response, para_b.get_next_page_url())
