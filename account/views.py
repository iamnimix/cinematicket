from pickle import FALSE

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions

from .serializer import UserSerializer, LoginSerializer, OtpVerificationSerializer, ProfileSerializer
from .tasks import send_otp
from .custom_permission import IsOwner

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


class OtpVerification(ViewSet):

    @action(detail=False, methods=['post'], name='otp', url_path='verification')
    def login_otp_verify(self, request):
        serializer = OtpVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data['otp']
        phone_number = request.COOKIES.get('phone_number')
        real_otp = cache.get(phone_number)

        if real_otp == int(otp):
            user = User.objects.get(phone=phone_number)
            refresh = RefreshToken.for_user(user)
            response = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProfileViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
