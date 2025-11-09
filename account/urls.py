from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.views import RegisterUser, LoginUser, OtpVerification, ProfileViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register('', LoginUser, basename='users')
router.register(r'', OtpVerification, basename='otp')

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('', include(router.urls)),
]
