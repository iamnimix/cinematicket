from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cinema'

router = DefaultRouter()
router.register(r'genre', views.GenreViewSet, basename='genre')
router.register(r'movie', views.MovieViewSet, basename='movie')
router.register(r'showtimes', views.ShowTimeViewSet, basename='showtime')
router.register(r'seat', views.SeatViewSet, basename='seat')
router.register(r'reserve', views.ReservationViewSet, basename='reserve')
router.register(r'payment', views.PaymentViewSet, basename='payment')


urlpatterns = [ path('', include(router.urls))]