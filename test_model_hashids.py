from unittest import TestCase
from unittest.mock import Mock, patch
from django.http import Http404
from hashids import Hashids
from model_hashids import HashidsMixin
from utils_for_testing import get_random_int


class HashidsMixinTests(TestCase):
    def get_test_class(self, hashids=None):

        class TestClass(HashidsMixin):
            def __init__(self, pk):
                self.id = pk

            if hashids is not None:
                _hashids = hashids

        return TestClass

    def test_encoding_and_then_decoding_hashid_returns_same_value(self):
        test_class = self.get_test_class()
        for pk in (get_random_int() for _ in range(10)):
            instance = test_class(pk)
            decoded = test_class.decode_hashid_or_404(instance.hashid)
            self.assertEqual(decoded, pk, "Failed to correctly encode and decode {}".format(pk))

    def test_decode_or_404_raises_404_error_when_hashid_does_not_decode(self):
        test_class = self.get_test_class()
        for hashid in ('ffd', '', 'sfoiwf'):
            with self.assertRaises(Http404):
                test_class.decode_hashid_or_404(hashid)

    def test_decode_or_404_raises_404_error_when_hashid_decodes_to_too_multiple_numbers(self):
        test_class = self.get_test_class()
        multiple_numbers = (
            (3, 346, 23),
            (1, 2),
            (32, 27, 97),
        )
        for numbers in multiple_numbers:
            with self.assertRaises(Http404):
                test_class.decode_hashid_or_404(numbers)

    @patch('model_hashids.get_object_or_404')
    def test_get_object_by_hashid_calls_decode_or_404_class_method(self, get_object_mock):
        pk = 17
        hashids = Hashids()
        test_class = self.get_test_class(hashids)
        test_class.get_by_hashid_or_404(hashids.encode(pk))
        get_object_mock.assert_called_once_with(test_class, pk=pk)

