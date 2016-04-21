from django.contrib.auth import authenticate, login, logout
from django.db.transaction import atomic
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.decorators import api_view, detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import UserSerializer, LoginDataSerializer, CreateUserSerializer
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        user.save()
        user = authenticate(username=user.username, password=serializer.data['password'])
        login(request, user)
        return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)


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
