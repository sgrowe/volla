from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import UserSerializer, LoginDataSerializer, CreateUserSerializer
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
        return Response(data=self.serializer_class(user).data, status=status.HTTP_201_CREATED)

    @list_route(["POST"])
    def logout(self, request):
        logout(request)
        return Response(data=self.serializer_class().data, status=status.HTTP_200_OK)

    @list_route(["POST"])
    def login(self, request):
        serializer = LoginDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise ValidationError(detail={'detail': ['Incorrect username or password.']})
        if not user.is_active:
            raise ValidationError(detail={'detail': ['Your account has been disabled. '
                                                     'Please email us if you think a mistake has been made.']})
        login(request, user)
        return Response(data=self.serializer_class(user).data, status=status.HTTP_200_OK)

    @list_route(['GET'])
    def logged_in(self, request):
        # Get the currently logged in user
        users = [request.user] if request.user.is_authenticated() else []
        serializer = self.get_serializer(users, many=True)
        self.paginate_queryset(users)  # initialise the paginator
        return self.get_paginated_response(serializer.data)
