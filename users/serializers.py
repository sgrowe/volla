from django.contrib.auth.models import User
from rest_framework import serializers
from stories.fields import HashidField
from hashids import Hashids


class LoginDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = HashidField(read_only=True, hashids=Hashids(min_length=4, salt=""))

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
