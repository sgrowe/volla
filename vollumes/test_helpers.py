from django.test import TestCase
from vollumes.helpers import get_users_most_recent_contributions
from utils_for_testing import create_and_save_dummy_user, create_and_save_dummy_vollume


class TestGetUsersMostRecentContributions(TestCase):
    def test_returns_users_contributions(self):
        user = create_and_save_dummy_user()
        vollume = create_and_save_dummy_vollume(author=user)
        contributions = get_users_most_recent_contributions(user)
        self.assertEqual(len(contributions), 1)
        self.assertEqual(contributions[0].vollume, vollume)
        self.assertEqual(len(contributions[0].items), 1)

    def test_orders_by_date_and_groups_by_vollume(self):
        user = create_and_save_dummy_user()
        vollume_a = create_and_save_dummy_vollume(author=user)
        vollume_a.first_paragraph.add_child(user, 'More words')
        vollume_b = create_and_save_dummy_vollume(author=user)
        vollume_a.first_paragraph.add_child(user, 'Something extra')
        contributions = get_users_most_recent_contributions(user)
        self.assertEqual(len(contributions), 3)
        self.assertEqual(contributions[0].vollume, vollume_a)
        self.assertEqual(contributions[1].vollume, vollume_b)
        self.assertEqual(contributions[2].vollume, vollume_a)
        self.assertEqual(contributions[0].items[0].text, 'Something extra')
        self.assertEqual(len(contributions[2].items), 2)
