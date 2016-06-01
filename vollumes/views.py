from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from csrf_exempt_viewsets import CsrfExemptModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotAuthenticated, ValidationError as RestValidationError
from django.core.urlresolvers import resolve
from django.db.transaction import atomic
from .models import Vollume, VollumeChunk, create_validate_and_save_vollume
from .serializers import VollumeSerializer, VollumeChunkSerializer, NewVollumeSerializer
from .filter_backends import query_params_filter
from contextlib import contextmanager


class HashidViewsetMixin:
    def get_object(self):
        # This is the same as the rest framework default except for the get_by_hashid_or_404 call

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {'hashid': self.kwargs[lookup_url_kwarg]}
        obj = self.model.get_by_hashid_or_404(**filter_kwargs, queryset=queryset)
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


@contextmanager
def rest_validation_errors():
    try:
        yield
    except ValidationError as error:
        raise RestValidationError(detail=error.message_dict)


def get_data(request, item):
    try:
        return request.data[item]
    except KeyError:
        raise ParseError


def get_by_url(model, url):
    try:
        return get_object_or_404(model, **resolve(url).kwargs)
    except Http404:
        raise ParseError(detail=['There is no {} at url {}'.format(model, url)])


def model_created_response(model):
    data = {
        'url': model.get_absolute_url(),
        'id': model.id,
    }
    return Response(data=data, status=status.HTTP_201_CREATED)


def get_logged_in_user(request):
    if not request.user.is_authenticated():
        raise NotAuthenticated
    return request.user


class VollumeViewSet(HashidViewsetMixin, CsrfExemptModelViewSet):
    model = Vollume
    queryset = Vollume.objects.all()
    serializer_class = VollumeSerializer

    def create(self, request):
        request_serializer = NewVollumeSerializer(data=request.data, context={'request': request})
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.data
        with rest_validation_errors():
            vollume = create_validate_and_save_vollume(
                author=get_logged_in_user(request),
                title=data['title'],
                text=data['text']
            )
        response_data = self.serializer_class(vollume, context={'request': request}).data
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class VollumeChunkViewSet(CsrfExemptModelViewSet):
    queryset = VollumeChunk.objects.all()
    serializer_class = VollumeChunkSerializer
