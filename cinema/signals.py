from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ShowTime, ReservationSeat

@receiver(post_save, sender=ShowTime)
def create_reservation_seats(sender, instance, created, **kwargs):
    if created:
        # وقتی یک ShowTime جدید ساخته شد، تمام صندلی‌های سالنش رو میگیریم
        seats = instance.hall.seats.all()

        # لیست ReservationSeat هایی که میخوایم بسازیم
        reservation_seats = [
            ReservationSeat(seat=seat, show_time=instance)
            for seat in seats
        ]

        # ساخت دسته‌ای در دیتابیس
        ReservationSeat.objects.bulk_create(reservation_seats)
