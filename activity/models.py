from django.conf import settings
from django.db import models
from django.utils import timezone


def new_activity(name, user):
    Activity(name=name, user=user).save()


class Activity(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    when = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '{} - {}'.format(self.name, self.user)
