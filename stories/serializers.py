from rest_framework import serializers
from .models import Vollume, VollumeStructure, Para
from .fields import HashidField
from hashids import Hashids


class VollumeStructureSerializer(serializers.HyperlinkedModelSerializer):
    id = HashidField(read_only=True)

    class Meta:
        model = VollumeStructure
        fields = ('id', 'author', 'story', 'order_in_story', 'para')


class VollumeSerializer(serializers.HyperlinkedModelSerializer):
    id = HashidField(read_only=True)

    class Meta:
        model = Vollume
        fields = ('id', 'created', 'author', 'title', 'structure')


class ParaSerializer(serializers.HyperlinkedModelSerializer):
    id = HashidField(read_only=True)

    class Meta:
        model = Para
        fields = ('id', 'text')
