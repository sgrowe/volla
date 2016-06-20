from django import template
from users.helpers import url_for_auth_view_which_returns_to_here

register = template.Library()


@register.simple_tag(takes_context=True)
def auth_redirect(context, url_name):
    request = context['request']
    url = url_for_auth_view_which_returns_to_here(url_name, request)
    return url
