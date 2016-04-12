from django.contrib.auth.models import User, Group
from .models import Vollume, VollumeStructure, Para
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class VollumeStructureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VollumeStructure
        fields = ('author', 'story', 'order_in_story', 'para')


class VollumeSerializer(serializers.HyperlinkedModelSerializer):
    structure = VollumeStructureSerializer(many=True)

    class Meta:
        model = Vollume
        fields = ('created', 'author', 'structure')


class ParaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Para
        fields = ('id', 'text')
