from unittest import mock
from django.test import TestCase
from django.http import Http404
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils import timezone
from model_hashids import HashidsMixin
from .models import Vollume, VollumeChunk, create_validate_and_save_vollume, get_paragraph_or_404
from utils_for_testing import create_and_save_dummy_user, create_and_save_dummy_vollume, get_random_int


class CreateVollumeHelperTests(TestCase):
    def test_create_vollume_helper_saves_new_vollumes(self):
        user = create_and_save_dummy_user()
        title = 'New vollume title'
        text = 'Text for the first paragraph'
        vollume = create_validate_and_save_vollume(author=user, title=title, text=text)
        self.assertIsNotNone(vollume.id)
        vollumes = Vollume.objects.all()
        self.assertEqual(len(vollumes), 1)
        self.assertEqual(vollumes[0].id, vollume.id)

    def test_create_vollume_helper_also_saves_first_paragraph(self):
        user = create_and_save_dummy_user()
        title = 'New vollume title'
        text = 'Text for the first paragraph'
        vollume = create_validate_and_save_vollume(author=user, title=title, text=text)
        # Check that the vollume and its first paragraph have been saved to the db
        self.assertIsNotNone(vollume.first_paragraph.id)
        chunks = VollumeChunk.objects.all()
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].vollume.id, vollume.id)

    def test_create_vollume_helper_does_not_save_on_errors(self):
        test_data = (
            (None, 'This is the vollume title', "This is the text of the first paragraph"),
            (create_and_save_dummy_user(username='The author'), None, 'Another first para'),
            (create_and_save_dummy_user(username='Another author'), 'You get the idea', None),
        )
        for data in test_data:
            with self.assertRaises(Exception):
                create_validate_and_save_vollume(*data)
            self.assertEqual(len(Vollume.objects.all()), 0)
            self.assertEqual(len(VollumeChunk.objects.all()), 0)

    @mock.patch.object(Vollume, 'full_clean')
    def test_create_vollume_helper_calls_full_clean_on_vollume(self, vollume_full_clean):
        user = create_and_save_dummy_user()
        title = 'New vollume title'
        text = 'Text for the first paragraph'
        create_validate_and_save_vollume(author=user, title=title, text=text)
        vollume_full_clean.assert_called_once_with()

    @mock.patch.object(VollumeChunk, 'full_clean')
    def test_create_vollume_helper_calls_full_clean_on_vollume_chunk(self, vollume_chunk_full_clean):
        user = create_and_save_dummy_user()
        title = 'New vollume title'
        text = 'Text for the first paragraph'
        create_validate_and_save_vollume(author=user, title=title, text=text)
        vollume_chunk_full_clean.assert_called_once_with()


class GetParentParagraphTests(TestCase):
    def setUp(self):
        self.vollume = create_and_save_dummy_vollume()
        self.child_paragraph = self.vollume.first_paragraph.add_child(
            self.vollume.author,
            'A whole load of words'
        )

    def test_raises_404_on_invalid_vollume_hashid(self):
        bad_hashids = (
            'fw45',
            '',
            '1',
        )
        for hashid in bad_hashids:
            self.assertNotEqual(hashid, self.vollume.hashid, 'Test has bad data. A test hashid accidentally matches '
                                                             'an actual hashid in the db: {}'.format(hashid))
            with self.assertRaises(Http404):
                get_paragraph_or_404(hashid, self.vollume.first_paragraph.hashid)

    def test_raises_404_on_invalid_paragraph_hashid(self):
        bad_hashids = (
            'fw45',
            '',
            '1',
        )
        paragraph_hashids = [paragraph.hashid for paragraph in VollumeChunk.objects.all()]
        for hashid in bad_hashids:
            self.assertNotIn(hashid, paragraph_hashids, 'Test has bad data. A test hashid accidentally matches '
                                                        'an actual hashid in the db: {}'.format(hashid))
            with self.assertRaises(Http404):
                get_paragraph_or_404(self.vollume.hashid, hashid)

    def test_returns_parent_paragraph_model(self):
        paragraph = get_paragraph_or_404(self.vollume.hashid, self.child_paragraph.hashid)
        self.assertEqual(paragraph, self.child_paragraph)


class VollumeTests(TestCase):
    def test_vollume_url_contains_its_hashid(self):
        vollume = create_and_save_dummy_vollume()
        for pk in (get_random_int() for _ in range(10)):
            vollume.pk = pk
            self.assertIn(vollume.hashid, vollume.get_absolute_url())

    def test_new_vollumes_have_an_accurate_creation_time_stamp(self):
        before = timezone.now()
        vollume = Vollume(
            title="You won't believe what happened once upon a time!",
            author=create_and_save_dummy_user()
        )
        vollume.save()
        after = timezone.now()
        self.assertIsNotNone(vollume.created)
        self.assertTrue(before < vollume.created < after)

    def test_vollume_title_is_required(self):
        vollume = Vollume(
            author=create_and_save_dummy_user()
        )
        with self.assertRaises(ValidationError) as caught:
            vollume.full_clean()
        validation_errors = caught.exception.message_dict
        self.assertIn('title', validation_errors)

    def test_vollume_author_is_required(self):
        vollume = Vollume(
            title='A riveting read'
        )
        with self.assertRaises(ValidationError) as caught:
            vollume.full_clean()
        validation_errors = caught.exception.message_dict
        self.assertIn('author', validation_errors)

    def test_vollume_str_method_shows_title(self):
        test_data = (
            ('A boshing good read', 'leeeroooy jeeenkinnnsss'),
            ('Title', 'user_person'),
        )
        for title, username in test_data:
            vollume = Vollume(
                title=title,
                author=create_and_save_dummy_user(username=username)
            )
            self.assertEqual(str(vollume), title)

    def test_vollume_uses_hashid_mixin(self):
        self.assertIsInstance(Vollume(), HashidsMixin)

    def test_vollume_hashid(self):
        vollume = create_and_save_dummy_vollume()
        hashids = (
            (4, 'YRzY'),
            (30, 'wvMj'),
            (39, 'j43Y'),
            (849, 'wG09'),
            (622, '83Bm'),
            (145944, '79JAO'),
            (26482746, 'qeNGoL'),
        )
        for pk, hashid in hashids:
            vollume.pk = pk
            self.assertEqual(vollume.hashid, hashid)

    def test_get_by_hashid_or_404(self):
        vollume = create_and_save_dummy_vollume()
        retrieved = Vollume.get_by_hashid_or_404(vollume.hashid)
        self.assertIsInstance(retrieved, Vollume)


class VollumeChunkTests(TestCase):
    def test_url_contains_parent_hashid(self):
        parent = create_and_save_dummy_vollume().first_paragraph
        child = parent.add_child(parent.author, "Cool uri's don't change man...")
        url = child.get_absolute_url()
        self.assertIn(parent.hashid, url)
        self.assertIn(child.vollume.hashid, url)

    def test_url_of_root_paragraph_is_vollume_url(self):
        vollume = create_and_save_dummy_vollume()
        self.assertEqual(vollume.first_paragraph.get_absolute_url(), vollume.get_absolute_url())

    def test_one_vollume_cant_have_multiple_root_chunks(self):
        vollume = create_and_save_dummy_vollume()
        new_chunk = VollumeChunk(
            vollume=vollume,
            author=create_and_save_dummy_user(username='Stevo'),
            text='top stuff'
        )
        with self.assertRaises(ValidationError) as caught:
            new_chunk.full_clean()
        error_messages = caught.exception.message_dict[NON_FIELD_ERRORS]
        self.assertIn("A Vollume can't have more than one starting paragraph.", error_messages)

    def test_add_child_method(self):
        vollume = create_and_save_dummy_vollume()
        new_chunk = vollume.first_paragraph.add_child(
            author=create_and_save_dummy_user(username='Hi guys'),
            text="It don't matter really"
        )
        self.assertIsNotNone(new_chunk.id)
        all_chunks = VollumeChunk.objects.all()
        self.assertEqual(len(all_chunks), 2)
        self.assertIn(new_chunk.id, (chunk.id for chunk in all_chunks))

    def test_author_of_first_chunk_must_also_be_vollume_author(self):
        vollume = Vollume(
            author=create_and_save_dummy_user(username='Mickey'),
            title='Top dollar mate'
        )
        vollume.save()
        chunk = VollumeChunk(
            vollume=vollume,
            author=create_and_save_dummy_user(username='Steves'),
            text="Huh? Yeah, I just feel like... you know when you roll a blinding spliff?"
        )
        with self.assertRaises(ValidationError) as caught:
            chunk.full_clean()
        error_messages = caught.exception.message_dict[NON_FIELD_ERRORS]
        self.assertIn("The author of the first paragraph of a Vollume must also be the Vollume author.", error_messages)

    def test_text_is_required(self):
        user = create_and_save_dummy_user()
        dummy_vollume = Vollume(
            author=user,
            title='Filler words, KILLER words',
        )
        dummy_vollume.save()
        for text in (None, ''):
            new_chunk = VollumeChunk(
                vollume=dummy_vollume,
                author=user,
                text=text
            )
            with self.assertRaises(ValidationError) as caught:
                new_chunk.full_clean()
            validation_errors = caught.exception.message_dict
            self.assertIn('text', validation_errors)

    def test_str_method_contains_vollume_title(self):
        vollume = create_and_save_dummy_vollume()
        self.assertIn(vollume.title, str(vollume.first_paragraph))

    def test_vollume_uses_hashid_mixin(self):
        self.assertIsInstance(VollumeChunk(), HashidsMixin)

    def test_vollume_chunk_hashids(self):
        hashids = (
            (21, '2rv2'),
            (54, 'LlyQ'),
            (65, '2rxv'),
            (87, '75P4'),
            (99, '2xY8'),
            (2, 'LDPL'),
            (222, '7no0'),
            (9414, 'dvdM'),
            (4466, 'n0OD'),
            (7226, 'KRXd'),
        )
        vollume_chunk = create_and_save_dummy_vollume().first_paragraph
        for pk, hashid in hashids:
            vollume_chunk.pk = pk
            self.assertEqual(vollume_chunk.hashid, hashid)

    def test_next_page_url(self):
        vollume = create_and_save_dummy_vollume()
        parent_paragraph = vollume.first_paragraph
        child = parent_paragraph.add_child(
            author=vollume.author,
            text='sjalfsrgbolr'
        )
        self.assertEqual(parent_paragraph.get_next_page_url(), child.get_absolute_url())
