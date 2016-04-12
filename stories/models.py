from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator


class Vollume(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='stories')
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title


class VollumeStructure(models.Model):
    story = models.ForeignKey(Vollume, related_name='structure')
    author = models.ForeignKey(User, related_name='contributions')
    order_in_story = models.IntegerField(validators=[MinValueValidator(1)])
    para = models.OneToOneField('Para')

    def __str__(self):
        return "{} - order {}".format(self.story.title, self.order_in_story)


class Para(models.Model):
    text = models.TextField(max_length=500)

    def __str__(self):
        return self.text
