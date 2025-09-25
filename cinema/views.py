from django.contrib.auth import login, authenticate
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Genre, Movie, ShowTime, Seat, Reservation, Payment, ReservationSeat
from .serializers import (
    GenreSerializer,
    MovieSerializer,
    ShowTimeSerializer,
    SeatSerializer,
    ReservationSerializer,
    PaymentSerializer,
)


class GenreViewSet(ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class MovieViewSet(ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ShowTimeViewSet(ReadOnlyModelViewSet):
    queryset = ShowTime.objects.all()
    serializer_class = ShowTimeSerializer

    @action(
        detail=True,
        methods=['get'],
        renderer_classes=[TemplateHTMLRenderer, JSONRenderer]
    )
    def available_seats(self, request, pk=None):
        show_time = self.get_object()
        available_seats = show_time.hall.seats.all()

        if request.accepted_renderer.format == 'json':
            serializer = SeatSerializer(available_seats, many=True)
            return Response(serializer.data)

        # برای HTML، سریالایزر رو هم می‌تونیم استفاده کنیم
        seats_serialized = SeatSerializer(available_seats, many=True).data
        showtime_serialized = ShowTimeSerializer(show_time).data

        return Response(
            {'seats': seats_serialized, 'show_time': showtime_serialized},
            template_name='available_seats.html'
        )

class SeatViewSet(ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        reservation = serializer.save()


        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"showtime_{reservation.show_time.id}",
            {
                'type': 'seat_update',
                'data': {
                    'action': 'reserved',
                    'seats': [s.id for s in reservation.seat.all()],
                    'status': reservation.status
                }
            }
        )



class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(status='success')
        payment.reservation.status = 'confirmed'
        payment.reservation.save()
