from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from .serializer import UserSerializer

User = get_user_model()
# Create your views here.


class RegisterUser(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
