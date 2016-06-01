from rest_framework import serializers
from .models import Vollume, VollumeChunk, create_validate_and_save_vollume


class VollumeChunkSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(read_only=True, source='hashid')

    class Meta:
        model = VollumeChunk
        fields = ('id', 'author', 'vollume', 'text')
        read_only = True


class VollumeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField(read_only=True, source='hashid')
    paragraphs = serializers.HyperlinkedRelatedField(
        view_name='paragraph-detail',
        many=True,
        read_only=True,
        source='structure'
    )

    class Meta:
        model = Vollume
        fields = ('id', 'created', 'author', 'title', 'paragraphs')
        read_only = True


class NewVollumeSerializer(serializers.Serializer):
    title = serializers.CharField()
    text = serializers.CharField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('title', 'text')
