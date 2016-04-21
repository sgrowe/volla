from rest_framework import serializers
from .models import Vollume, VollumeStructure, Para


class ParaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Para
        fields = ('id', 'text')


class VollumeStructureSerializer(serializers.HyperlinkedModelSerializer):
    para = ParaSerializer()

    class Meta:
        model = VollumeStructure
        fields = ('id', 'author', 'vollume', 'page', 'para')


class VollumeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Vollume
        fields = ('id', 'created', 'author', 'title', 'structure')
        read_only_fields = ('structure',)
