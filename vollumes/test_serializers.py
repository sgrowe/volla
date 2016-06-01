from .serializers import VollumeSerializer, VollumeChunkSerializer
from utils_for_testing import create_and_save_dummy_vollume
from django.test import TestCase, RequestFactory


class VollumeSerializerTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_hashid_is_in_serialized_data(self):
        request = self.rf.get('/')
        vollume = create_and_save_dummy_vollume()
        data = VollumeSerializer(vollume, context={'request': request}).data
        self.assertIn('id', data)
        self.assertEqual(data['id'], vollume.hashid)


class VollumeChunkSerializerTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_hashid_is_in_serialized_data(self):
        request = self.rf.get('/')
        vollume_chunk = create_and_save_dummy_vollume().first_chunk
        data = VollumeChunkSerializer(vollume_chunk, context={'request': request}).data
        self.assertIn('id', data)
        self.assertEqual(data['id'], vollume_chunk.hashid)
