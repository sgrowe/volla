from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.urlresolvers import resolve
from django.db.transaction import atomic
from .models import Vollume, VollumeStructure, Para
from .serializers import VollumeSerializer, VollumeStructureSerializer
from .filter_backends import query_params_filter


class VollumeViewSet(viewsets.ModelViewSet):
    queryset = Vollume.objects.all()
    serializer_class = VollumeSerializer

    def create(self, request):
        vollume = Vollume(
            author=request.user,
            title=request.data['title']
        )
        vollume.save()
        serializer = VollumeSerializer(vollume, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ParagraphViewSet(viewsets.ModelViewSet):
    queryset = VollumeStructure.objects.all()
    serializer_class = VollumeStructureSerializer
    filter_backends = (query_params_filter('story'), query_params_filter('page'))

    def create(self, request):
        vollume = Vollume.objects.get(**resolve(request.data['vollume']).kwargs)
        with atomic():
            para = Para(text=request.data['text'])
            para.save()
            structure = VollumeStructure(
                author=request.user,
                vollume=vollume,
                page=request.data['page'],
                para=para
            )
            structure.save()
        serializer = VollumeStructureSerializer(structure, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

