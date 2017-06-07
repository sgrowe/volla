from itertools import groupby
from operator import attrgetter


def get_users_most_recent_contributions(user):
    contributions = user.contributions.order_by('-created')
    grouped_by_vollume = groupby(contributions, key=attrgetter('vollume'))
    return [ContributionsGroup(g[0], list(g[1])) for g in grouped_by_vollume]


class ContributionsGroup:
    def __init__(self, vollume, items):
        self.vollume = vollume
        self.items = items
