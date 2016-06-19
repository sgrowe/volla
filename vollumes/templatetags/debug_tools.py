from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter('escape_angle_brackets_only')
def escape_angle_brackets_only(text):
    return mark_safe(text.replace('<', '&lt;').replace('>', '&gt;'))
