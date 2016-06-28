from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from users.models import User
from model_hashids import HashidsMixin
from hashids import Hashids
import re


def get_paragraph_or_404(vollume_hashid, paragraph_hashid):
    vollume_id = Vollume.decode_hashid_or_404(vollume_hashid)
    paragraph_id = VollumeChunk.decode_hashid_or_404(paragraph_hashid)
    query = VollumeChunk.objects.filter(vollume_id=vollume_id)
    return get_object_or_404(query, id=paragraph_id)


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
        return reverse('vollume', kwargs={'vollume_id': self.hashid})

    @property
    def first_paragraph(self):
        return self.structure.get(parent=None)


class VollumeChunk(HashidsMixin, models.Model):
    vollume = models.ForeignKey(Vollume, related_name='structure')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    author = models.ForeignKey(User, related_name='contributions')
    text = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(500)])

    def __str__(self):
        return "{} - {}".format(self.vollume, self.text)

    hashids = Hashids(salt='Do or do not; there is no try.', min_length=4)

    def get_absolute_url(self):
        if self.parent is not None:
            return self.parent.get_next_page_url()
        else:
            return self.vollume.get_absolute_url()

    def get_next_page_url(self):
        return reverse('vollume-page', kwargs={'vollume_id': self.vollume.hashid, 'paragraph_id': self.hashid})

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

    def text_as_html(self):
        return mark_safe(''.join(self._format_paragraphs()))

    def _format_paragraphs(self):
        text = self.text.replace('\r\n', '\n')
        for paragraph in re.split(r'\n{2,}', text):
            paragraph = escape(paragraph).replace('\n', '<br>')
            yield '<p class="margin-top">{}</p>'.format(paragraph)

    def clean(self):
        super().clean()
        self._ensure_vollume_has_only_one_first_para()
        self._ensure_first_para_author_is_also_vollume_author()

    def _ensure_vollume_has_only_one_first_para(self):
        if self.parent is None:  # then this is the first para
            try:
                if self.vollume.first_paragraph.id != self.id:
                    raise ValidationError("A Vollume can't have more than one starting paragraph.")
            except ObjectDoesNotExist:
                pass

    def _ensure_first_para_author_is_also_vollume_author(self):
        if self.parent is None and self.vollume.author.id != self.author.id:
            raise ValidationError("The author of the first paragraph of a Vollume must also be the Vollume author.")
