from rest_framework import serializers
from rest_framework import exceptions as restful_exceptions
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
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
        try:
            password = validated_data['password']
            validate_password(password)
        except ValidationError as error:
            raise restful_exceptions.ValidationError(detail={'password': error.messages})
        user.set_password(password)
        return user


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
