from django.core.urlresolvers import resolve
from django.db.transaction import atomic
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Vollume, VollumeStructure, Para
from .serializers import VollumeSerializer, VollumeStructureSerializer
from .filter_backends import query_params_filter


class VollumeViewSet(viewsets.ModelViewSet):
    queryset = Vollume.objects.all()
    serializer_class = VollumeSerializer


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
                author=self.request.user,
                vollume=vollume,
                page=request.data['page'],
                para=para
            )
            structure.save()
        serializer = VollumeStructureSerializer(structure, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

