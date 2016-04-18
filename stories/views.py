from rest_framework import viewsets
from .models import Vollume, VollumeStructure, Para
from .serializers import VollumeSerializer, VollumeStructureSerializer, ParaSerializer


class VollumeViewSet(viewsets.ModelViewSet):
    queryset = Vollume.objects.all()
    serializer_class = VollumeSerializer


class VollumeStructureViewSet(viewsets.ModelViewSet):
    queryset = VollumeStructure.objects.all()
    serializer_class = VollumeStructureSerializer


class ParaViewSet(viewsets.ModelViewSet):
    queryset = Para.objects.all()
    serializer_class = ParaSerializer
