from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.core.urlresolvers import resolve
from django.db.transaction import atomic
from .models import Vollume, VollumeStructure, Para
from .serializers import VollumeSerializer, VollumeStructureSerializer
from .filter_backends import query_params_filter


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


class VollumeViewSet(viewsets.ModelViewSet):
    queryset = Vollume.objects.all()
    serializer_class = VollumeSerializer

    def create(self, request):
        title = get_data(request, 'title')
        vollume = Vollume(
            author=request.user,
            title=title
        )
        vollume.save()
        return model_created_response(vollume)


class ParagraphViewSet(viewsets.ModelViewSet):
    queryset = VollumeStructure.objects.all()
    serializer_class = VollumeStructureSerializer
    filter_backends = (query_params_filter('story'), query_params_filter('page'))

    def create(self, request):
        vollume = get_by_url(Vollume, get_data(request, 'vollume'))
        with atomic():
            para = Para(text=get_data(request, 'text'))
            para.save()
            structure = VollumeStructure(
                author=request.user,
                vollume=vollume,
                page=get_data(request, 'page'),
                para=para
            )
            structure.save()
        serializer = VollumeStructureSerializer(structure, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

