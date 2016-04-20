from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator
from django.core.urlresolvers import reverse


class Vollume(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='vollumes')
    title = models.CharField(max_length=150, validators=[MinLengthValidator(1)])
    # allows_forks = models.BooleanField()
    # allows_alternatives_paras = models.BooleanField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('vollume-detail', kwargs={'pk': self.id})


class VollumeStructure(models.Model):
    vollume = models.ForeignKey(Vollume, related_name='structure')
    author = models.ForeignKey(User, related_name='contributions')
    page = models.IntegerField(validators=[MinValueValidator(1)])
    para = models.OneToOneField('Para')

    def __str__(self):
        return "{} - page {}".format(self.vollume.title, self.page)


class Para(models.Model):
    text = models.TextField(max_length=500, validators=[MinLengthValidator(1)])

    def __str__(self):
        return self.text
