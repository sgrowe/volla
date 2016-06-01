from users.models import User
from vollumes.models import create_validate_and_save_vollume
# TODO: Investigate a better way of using random numbers in unit tests (for repeatability)
from random import random, randint


def get_random_int():
    return randint(1, 100000)


def test_server_url(item):
    return 'http://testserver' + item.get_absolute_url()


def create_and_save_dummy_user(**kwargs):
    kwargs.setdefault('username', 'some_user')
    password = kwargs.pop('password', 'password123')
    user = User(**kwargs)
    user.set_password(password)
    user.save()
    return user


def create_and_save_dummy_vollume(**kwargs):
    if 'author' not in kwargs:
        kwargs['author'] = create_and_save_dummy_user()
    kwargs.setdefault('title', "You won't believe what she said next!")
    kwargs.setdefault('text', 'Some words and words and words...')
    return create_validate_and_save_vollume(**kwargs)
