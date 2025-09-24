from django.db import transaction, IntegrityError
from django.utils import timezone
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

        # 🔒 قفل برای جلوگیری از race condition
        try:
            with transaction.atomic():
                reserved_seats = ReservationSeat.objects.select_for_update().filter(
                    seat__in=seats,
                    show_time=showtime,
                    reservation__status__in=["pending", "confirmed"],
                    reservation__expires_at__gt=timezone.now()
                )
                if reserved_seats.exists():
                    raise serializers.ValidationError("یکی از صندلی‌ها قبلاً رزرو شده است!")

                reservation = Reservation.objects.create(user=user, **validated_data)
                ReservationSeat.objects.bulk_create([
                    ReservationSeat(reservation=reservation, seat=seat, show_time=showtime)
                    for seat in seats
                ])
        except IntegrityError:
            raise serializers.ValidationError("❌ خطا در ثبت رزرو، لطفاً دوباره تلاش کنید.")

        return reservation


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
