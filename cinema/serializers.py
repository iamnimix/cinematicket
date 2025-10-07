from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers
from .models import Genre, Movie, Hall, ShowTime, Seat, Reservation, Payment, ReservationSeat


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "name", "genre"]


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = "__all__"


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "row", "number"]


class ShowTimeSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField()
    hall = serializers.StringRelatedField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = ShowTime
        fields = ["id", "start_time", "end_time", "movie", "hall", "available_seats"]

    def get_available_seats(self, obj):
        reserved_seats = Reservation.objects.filter(
            show_time=obj,
            status__in=["pending", "confirmed"]
        ).values_list("seat", flat=True)

        return SeatSerializer(obj.hall.seats.exclude(id__in=reserved_seats), many=True).data


class ReservationSerializer(serializers.ModelSerializer):
    seat = serializers.PrimaryKeyRelatedField( many=True, queryset=Seat.objects.all())

    class Meta:
        model = Reservation
        fields = ('id', 'user', 'show_time', 'seat', 'status', 'created_at', 'expires_at')
        read_only_fields = ('user', 'status', 'created_at', 'expires_at')

    def create(self, validated_data):
        seats = validated_data.pop("seat")
        user = self.context["request"].user
        showtime = validated_data["show_time"]
        try:
            with transaction.atomic():
                # Lock all related ReservationSeat records
                locked_seats = ReservationSeat.objects.filter(
                    seat__in=seats,
                    show_time=showtime
                ).select_for_update()
                for seat in locked_seats:
                    pass

                # If not all seats are found, raise an error
                if locked_seats.count() != len(seats):
                    print(f"[{user}] خطا: برخی از صندلی‌ها یافت نشدند.")
                    raise serializers.ValidationError("برخی از صندلی‌ها یافت نشدند.")

                # Check if any are already reserved
                if locked_seats.filter(reservation__status__in=['pending', 'confirmed']).exists():
                    print(f"[{user}] خطا: برخی صندلی‌ها قبلاً رزرو شده‌اند.")
                    raise serializers.ValidationError("برخی صندلی‌ها قبلاً رزرو شده‌اند.")


                # Create reservation
                reservation = Reservation.objects.create(user=user, **validated_data)

                # Update ReservationSeat records
                updated = locked_seats.filter(reservation__isnull=True).update(reservation=reservation)
                if not updated:
                    updated = locked_seats.filter(reservation__status='cancelled').update(reservation=reservation)
                if updated != len(seats):
                    print(f"[{user}] خطا در رزرو صندلی‌ها، تعداد به‌روزرسانی‌ها کمتر از تعداد صندلی‌ها است.")
                    raise serializers.ValidationError("خطا در رزرو صندلی‌ها، لطفاً دوباره تلاش کنید.")

        except IntegrityError:
            raise serializers.ValidationError("❌ خطا در ثبت رزرو، لطفاً دوباره تلاش کنید.")

        return reservation


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ('transaction_id',)
