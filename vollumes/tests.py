from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from django.contrib.auth.models import User
from .models import Vollume
# from .fields import HashidAutoField
#
#
# class HashidFieldTest(SimpleTestCase):
#     def test_to_db_value(self):
#         field = HashidAutoField()
#         self.assertEqual(field.get_prep_value('oj'), 6)


def user_url(user):
    """
    :type user: User
    :param user: The user to get the url for
    :return: The absolute url for that user (but excluding the domain name)
    """
    return reverse('user-detail', kwargs={'pk': user.id})


class VollumeApiTest(APITestCase):

    def test_vollumes_list(self):
        url = reverse('vollume-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User(username="test user", email="test@volla.co")
        user.save()
        title = "nsapsdjf"
        vollume = Vollume(author=user, title=title)
        vollume.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.data
        self.assertEqual(json['count'], len(json['results']))
        self.assertEqual(json['results'][0]['title'], title)

    def test_create_vollume(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        author_url = user_url(author)
        post_data = {
            'author': author_url,
            'title': "A great story",
        }
        url = reverse('vollume-list')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.data
        self.assertTrue(json['author'].endswith(author_url))
        self.assertEqual(json['title'], "A great story")
        self.assertEqual(len(json['structure']), 0)


class ParagraphApiTest(APITestCase):

    def test_create_paragraph(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        vollume = Vollume(author=author, title="A tale of two tests")
        vollume.save()
        url = reverse('paragraph-list')
        post_data = {
            'vollume': vollume.get_absolute_url(),
            'page': 1,
            'text': "Some brilliant words!"
        }
        self.client.force_login(author)
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.data
        self.assertEqual(json['page'], 1)
        self.assertTrue(json['author'].endswith(user_url(author)))
        self.assertEqual(json['para']['text'], "Some brilliant words!")
        #
        # self.assertEqual()
        # self.assertIn('author', response.data)
        # self.assertIn('vollume', response.data)
        # self.assertIn('page', response.data)
