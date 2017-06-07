from django.test import TestCase
from django.utils import timezone

from utils_for_testing import create_and_save_dummy_user
from activity.models import new_activity, Activity


class NewActivityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_and_save_dummy_user()

    def test_creates_one_new_activity_in_db(self):
        self.assertEqual(Activity.objects.count(), 0)
        new_activity('login', self.user)
        self.assertEqual(Activity.objects.count(), 1)

    def test_activity_is_associated_with_the_given_user(self):
        new_activity('', self.user)
        self.assertEqual(Activity.objects.filter(user=self.user).count(), 1)

    def test_created_activity_has_the_given_name(self):
        name = 'ford'
        new_activity(name, self.user)
        self.assertEqual(Activity.objects.filter(name=name).count(), 1)

    def test_stores_created_time(self):
        before = timezone.now()
        new_activity('satsuma', self.user)
        after = timezone.now()
        activity = Activity.objects.all()[0]
        self.assertTrue(before < activity.when < after)
