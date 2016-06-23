from django.conf import settings
from django.template import library
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = library.Library()


@register.simple_tag()
def email():
    email = escape(settings.SUPPORT_EMAIL)
    encoded = ''.join('&#{};'.format(ord(char)) for char in email)
    return mark_safe('<a href="mailto:{0}">{0}</a>'.format(encoded))
