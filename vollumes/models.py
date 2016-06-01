from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.utils import timezone
from users.models import User
from model_hashids import HashidsMixin
from hashids import Hashids


def create_validate_and_save_vollume(author, title, text):
    with atomic():
        vollume = Vollume(
            author=author,
            title=title
        )
        vollume.full_clean()
        vollume.save()
        vollume_chunk = vollume.structure.create(
            author=author,
            text=text
        )
        vollume_chunk.full_clean()
    return vollume


class Vollume(HashidsMixin, models.Model):
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, related_name='vollumes')
    title = models.CharField(max_length=150, validators=[MinLengthValidator(1)])
    # allows_forks = models.BooleanField()
    # allows_alternative_paras = models.BooleanField()

    def __str__(self):
        return self.title

    hashids = Hashids(salt='leeerooooy jeeenkinnnsss', min_length=4)

    def get_absolute_url(self):
        return reverse('vollume-detail', kwargs={'pk': self.hashid})

    @property
    def first_chunk(self):
        return self.structure.get(parent=None)


class VollumeChunk(HashidsMixin, models.Model):
    vollume = models.ForeignKey(Vollume, related_name='structure')
    parent = models.ForeignKey('self', null=True, blank=True)
    author = models.ForeignKey(User, related_name='contributions')
    text = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(500)])

    def __str__(self):
        return "{} - {}".format(self.vollume, self.text)

    hashids = Hashids(salt='Do or do not; there is no try.', min_length=4)

    def get_absolute_url(self):
        return reverse('paragraph-detail', kwargs={'pk': self.hashid})

    def clean(self):
        super().clean()
        self._ensure_vollume_has_only_one_first_para()
        self._ensure_first_para_author_is_also_vollume_author()

    def _ensure_vollume_has_only_one_first_para(self):
        if self.parent is None:  # then this is the first para
            try:
                first_para = self.vollume.first_chunk
                if first_para.id != self.id:
                    raise ValidationError("A Vollume can't have more than one starting paragraph.")
            except VollumeChunk.DoesNotExist:
                pass

    def _ensure_first_para_author_is_also_vollume_author(self):
        if self.parent is None and self.vollume.author.id != self.author.id:
            raise ValidationError("The author of the first paragraph of a Vollume must also be the Vollume author.")

    def add_child(self, author, text):
        child = VollumeChunk(
            vollume=self.vollume,
            parent=self,
            author=author,
            text=text
        )
        child.full_clean()
        child.save()
        return child

