from django.test import TestCase
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from vollumes.serializers import VollumeStructureSerializer, VollumeSerializer
from .models import Vollume, VollumeStructure, Para
from .models import User
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
    return 'http://testserver' + reverse('user-detail', kwargs={'pk': user.id})


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
        self.assertEqual(len(json['results']), 1)
        first_result = json['results'][0]
        self.assertIn('id', first_result)
        self.assertIn('created', first_result)
        self.assertEqual(first_result['author'], user_url(user))
        self.assertEqual(first_result['title'], title)
        self.assertIn('structure', first_result)

    def test_vollume_detail(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        title = "egjtpogjf"
        vollume = Vollume(author=author, title=title)
        vollume.save()
        url = reverse('vollume-detail', kwargs={'pk': vollume.id})
        para_a_text = "A great paragraph"
        para_a = Para(text=para_a_text)
        para_a.save()
        structure_a = VollumeStructure(vollume=vollume, author=author, page=1, para=para_a)
        structure_a.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.data
        self.assertIn('id', json)
        self.assertIn('created', json)
        self.assertEqual(json['author'], user_url(author))
        self.assertEqual(json['title'], title)
        self.assertEqual(len(json['structure']), 1)
        self.assertEqual(json['structure'][0], 'http://testserver' + structure_a.get_absolute_url())

    def test_anonymous_users_cant_create_vollumes(self):
        post_data = {
            'author': "",
            'title': "A great story",
        }
        url = reverse('vollume-list')
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_vollume(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        self.client.force_login(author)
        url = reverse('vollume-list')
        response = self.client.post(url, {'bad_data': 'rghd'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        post_data = {
            'title': "A great story",
        }
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Vollume.objects.all()), 1)
        self.assertEqual(response.data['url'], Vollume.objects.all()[0].get_absolute_url())
        response = self.client.get(response.data['url'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.data
        self.assertEqual(json['author'], user_url(author))
        self.assertEqual(json['title'], "A great story")
        self.assertEqual(len(json['structure']), 0)


class ParagraphApiTest(APITestCase):

    def test_list_paragraphs(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        vollume = Vollume(author=author, title="A tale of two tests")
        vollume.save()
        para_a = Para(text="A great paragraph")
        para_a.save()
        structure_a = VollumeStructure(vollume=vollume, author=author, page=1, para=para_a)
        structure_a.save()
        response = self.client.get(reverse('paragraph-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_users_cant_create_paragraphs(self):
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
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(json['author'], user_url(author))
        self.assertEqual(json['para']['text'], "Some brilliant words!")


class ApiFlowsTest(APITestCase):
    def create_vollume_with_paragraphs(self):
        author = User(username="test user", email="test@volla.co")
        author.save()
        self.client.force_login(author)
        post_data = {
            'title': "A great story",
        }
        response = self.client.post(reverse('vollume-list'), post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.data
        self.assertEqual(json['author'], user_url(author))
        self.assertEqual(json['title'], "A great story")
        self.assertEqual(len(json['structure']), 0)
