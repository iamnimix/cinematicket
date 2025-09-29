from pickle import FALSE

from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from  rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from .serializer import UserSerializer, LoginSerializer
from .tasks import send_otp

User = get_user_model()
# Create your views here.


class RegisterUser(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginUser(ViewSet):

    @action(detail=False, methods=['post'], name='login', url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        phone_number = user.phone
        send_otp.delay(phone_number)

        response = Response(status=status.HTTP_200_OK, data={'detail': 'Otp sent'})
        response.set_cookie('phone_number', phone_number)
        print(response.cookies.get('phone_number'))
        return response
