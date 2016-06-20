from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse


def url_for_auth_view_which_returns_to_here(page, request, query_param_name=REDIRECT_FIELD_NAME):
    return '{url}?{param_name}={param_value}'.format(
        url=reverse(page),
        param_name=query_param_name,
        param_value=request.get_full_path()
    )
