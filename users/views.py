from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from rest_framework import viewsets
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .serializers import UserSerializer, LoginDataSerializer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["GET"])
def get_current_user(request):
    if request.user.is_authenticated():
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    else:
        raise Http404


@api_view(["POST"])
def login_view(request):
    print("login")
    stream = BytesIO(request.body)
    data = JSONParser().parse(stream)
    serializer = LoginDataSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = authenticate(username=data['username'], password=data['password'])
    if user is None:
        print("Invalid credentials")
        raise ValidationError("Invalid username or password.")
    if not user.is_active:
        print("Account inactive")
        raise ValidationError("Account has not been activated yet.")
    login(request, user)
    response_serializer = UserSerializer(user)
    return Response(response_serializer.data)


@api_view(["POST"])
def logout_view(request):
    logout(request)
    return Response()
