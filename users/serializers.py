from rest_framework import serializers
from vollumes.fields import HashidField
from hashids import Hashids
from .models import User


class LoginDataSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        return user


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
