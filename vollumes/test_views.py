from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from utils_for_testing import create_and_save_dummy_vollume, create_and_save_dummy_user
from .models import Vollume, VollumeChunk


class CreateVollumeApiTests(APITestCase):
    def setUp(self):
        self.url = reverse('vollume-list')
        self.post_data = {
            'title': 'Khdksjfhkd',
            'text': 'lfdghflkgh',
        }

    def send_request(self, assert_status=status.HTTP_201_CREATED):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, assert_status)
        return response

    def test_create_vollume_response_contains_vollume_id(self):
        self.client.force_login(create_and_save_dummy_user())
        response = self.send_request()
        vollume = Vollume.objects.first()
        self.assertEqual(response.data['id'], vollume.hashid)

    def test_must_be_logged_in_to_create_vollume(self):
        self.send_request(assert_status=status.HTTP_403_FORBIDDEN)

    def test_create_vollume_saves_vollume_with_posted_title(self):
        self.client.force_login(create_and_save_dummy_user())
        response = self.send_request()
        vollumes = Vollume.objects.all()
        self.assertEqual(len(vollumes), 1)
        self.assertEqual(vollumes[0].title, self.post_data['title'])

    def test_create_vollume_saves_vollume_chunk_with_posted_text(self):
        user = create_and_save_dummy_user()
        self.client.force_login(user)
        response = self.send_request()
        vollume_chunks = VollumeChunk.objects.all()
        self.assertEqual(len(vollume_chunks), 1)
        self.assertEqual(vollume_chunks[0].text, self.post_data['text'])

    def test_title_required(self):
        del self.post_data['title']
        self.client.force_login(create_and_save_dummy_user())
        response = self.send_request(assert_status=status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_title_max_length_enforced(self):
        self.client.force_login(create_and_save_dummy_user())
        self.post_data['title'] += 'a' * (Vollume._meta.get_field('title').max_length + 1)
        response = self.send_request(assert_status=status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)


class VollumesListApiTests(APITestCase):
    def setUp(self):
        self.url = reverse('vollume-list')

    def get_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_vollume_list_empty_when_no_vollumes(self):
        response = self.get_response()
        self.assertEqual(response.data['results'], [])

    def test_vollume_list_mutiple_vollumes(self):
        vollume_data = (
            ('A brilliant Vollume', 'Some words to go in it', 'Og2Pro'),
            ('greigj', 'fgsg', 'wrgiwr'),
            ('dbsnyrnrsy', 'gsdgsdg', 'wgr;jer'),
        )
        for title, text, username in vollume_data:
            create_and_save_dummy_vollume(
                title=title,
                text=text,
                author=create_and_save_dummy_user(username=username)
            )
        response = self.get_response()
        self.assertEqual(len(response.data['results']), len(vollume_data))


class VollumeDetailApiTests(APITestCase):
    def test_get_vollume_contains_paragraph_urls(self):
        author = create_and_save_dummy_user()
        vollume = create_and_save_dummy_vollume(
            author=author
        )
        for para in ('kfhgfkjgh', 'adoiqr0298rewfn', 'rt24fjvlbem[23oq'):
            chunk = VollumeChunk(author=author, text=para, parent=vollume.first_chunk, vollume=vollume)
            chunk.save()
        response = self.client.get(vollume.get_absolute_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('paragraphs', response.data)
        paras = response.data['paragraphs']
        self.assertEqual(len(paras), 4)
        for chunk_url in paras:
            response = self.client.get(chunk_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateParagraphApiTests(APITestCase):
    pass

# class VollumeApiTest(APITestCase):
#
#     def test_vollumes_list(self):
#         url = reverse('vollume-list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         user = User(username="test user", email="test@volla.co")
#         user.save()
#         title = "nsapsdjf"
#         vollume = Vollume(author=user, title=title)
#         vollume.save()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         json = response.data
#         self.assertEqual(len(json['results']), 1)
#         first_result = json['results'][0]
#         self.assertIn('id', first_result)
#         self.assertIn('created', first_result)
#         self.assertEqual(first_result['author'], user_url(user))
#         self.assertEqual(first_result['title'], title)
#         self.assertIn('structure', first_result)
#
#     def test_vollume_detail(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         title = "egjtpogjf"
#         vollume = Vollume(author=author, title=title)
#         vollume.save()
#         url = reverse('vollume-detail', kwargs={'pk': vollume.id})
#         para_a_text = "A great paragraph"
#         para_a = Para(text=para_a_text)
#         para_a.save()
#         structure_a = VollumeChunk(vollume=vollume, author=author, page=1, para=para_a)
#         structure_a.save()
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         json = response.data
#         self.assertIn('id', json)
#         self.assertIn('created', json)
#         self.assertEqual(json['author'], user_url(author))
#         self.assertEqual(json['title'], title)
#         self.assertEqual(len(json['structure']), 1)
#         self.assertEqual(json['structure'][0], 'http://testserver' + structure_a.get_absolute_url())
#
#     def test_anonymous_users_cant_create_vollumes(self):
#         post_data = {
#             'author': "",
#             'title': "A great story",
#         }
#         url = reverse('vollume-list')
#         response = self.client.post(url, post_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_create_vollume(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         self.client.force_login(author)
#         url = reverse('vollume-list')
#         response = self.client.post(url, {'bad_data': 'rghd'}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         post_data = {
#             'title': "A great story",
#         }
#         response = self.client.post(url, post_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(len(Vollume.objects.all()), 1)
#         self.assertEqual(response.data['url'], Vollume.objects.all()[0].get_absolute_url())
#         response = self.client.get(response.data['url'])
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         json = response.data
#         self.assertEqual(json['author'], user_url(author))
#         self.assertEqual(json['title'], "A great story")
#         self.assertEqual(len(json['structure']), 0)
#
#
# class ParagraphApiTest(APITestCase):
#
#     def test_list_paragraphs(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         vollume = Vollume(author=author, title="A tale of two tests")
#         vollume.save()
#         para_a = Para(text="A great paragraph")
#         para_a.save()
#         structure_a = VollumeChunk(vollume=vollume, author=author, page=1, para=para_a)
#         structure_a.save()
#         response = self.client.get(reverse('paragraph-list'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_anonymous_users_cant_create_paragraphs(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         vollume = Vollume(author=author, title="A tale of two tests")
#         vollume.save()
#         url = reverse('paragraph-list')
#         post_data = {
#             'vollume': vollume.get_absolute_url(),
#             'page': 1,
#             'text': "Some brilliant words!"
#         }
#         response = self.client.post(url, post_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_create_paragraph(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         vollume = Vollume(author=author, title="A tale of two tests")
#         vollume.save()
#         url = reverse('paragraph-list')
#         post_data = {
#             'vollume': vollume.get_absolute_url(),
#             'page': 1,
#             'text': "Some brilliant words!"
#         }
#         self.client.force_login(author)
#         response = self.client.post(url, post_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         json = response.data
#         self.assertEqual(json['page'], 1)
#         self.assertEqual(json['author'], user_url(author))
#         self.assertEqual(json['para']['text'], "Some brilliant words!")
#
#
# class ApiFlowsTest(APITestCase):
#     def create_vollume_with_paragraphs(self):
#         author = User(username="test user", email="test@volla.co")
#         author.save()
#         self.client.force_login(author)
#         post_data = {
#             'title': "A great story",
#         }
#         response = self.client.post(reverse('vollume-list'), post_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         json = response.data
#         self.assertEqual(json['author'], user_url(author))
#         self.assertEqual(json['title'], "A great story")
#         self.assertEqual(len(json['structure']), 0)
