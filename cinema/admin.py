from django.contrib import admin
from .models import Genre, Movie, Hall, ShowTime, Seat, Reservation, ReservationSeat, Payment


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("name", "genre")
    list_filter = ("genre",)
    search_fields = ("name",)


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity")
    search_fields = ("name",)


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "hall", "start_time", "end_time")
    list_filter = ("movie", "hall")
    search_fields = ("movie__name", "hall__name")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("id", "hall", "row", "number")
    list_filter = ("hall",)
    search_fields = ("hall__name",)


class ReservationSeatInline(admin.TabularInline):
    model = ReservationSeat
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("user", "show_time", "status", "created_at", "expires_at")
    list_filter = ("status", "show_time__movie")
    search_fields = ("user__username", "show_time__movie__name")
    inlines = [ReservationSeatInline]


@admin.register(ReservationSeat)
class ReservationSeatAdmin(admin.ModelAdmin):
    list_display = ('reservation',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "reservation", "amount", "transaction_id", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("transaction_id", "reservation__user__username")
