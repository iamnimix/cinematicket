from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from .models import Reservation
from django.utils import timezone


@shared_task()
def release_expired_reservations():
    expired_qs = Reservation.objects.filter( status="pending", expires_at__lt=timezone.now() )
    channel_layer = get_channel_layer()
    for reservation in expired_qs:
        reservation.status = "cancelled"
        reservation.save()
        async_to_sync(channel_layer.group_send)(
            f"showtime_{reservation.show_time.id}",
            {
                "type": "seat_update",
                "data": {
                    "action": "cancelled",
                    "seats": [s.id for s in reservation.seat.all()],
                },
            }
        )
    return f"{expired_qs.count()} expired reservations cancelled"
