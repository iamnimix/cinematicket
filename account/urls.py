from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.views import RegisterUser, LoginUser

router = DefaultRouter()
router.register('', LoginUser, basename='users')

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('', include(router.urls)),
]
