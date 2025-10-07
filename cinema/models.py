import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(models.Model):
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        related_name='movies',
        related_query_name='movie',
        null = True
    )

    def __str__(self):
        return self.name


class Hall(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class ShowTime(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='times')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='times')


    def __str__(self):
        return f"hall({self.hall.name})-movie({self.movie.name}),{self.start_time}"


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats')
    row = models.PositiveIntegerField()
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.row}row-{self.number}seat ({self.hall.name})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    show_time = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='reservations')
    seat = models.ManyToManyField(Seat, related_name='reservations', through="ReservationSeat")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=1))

    def __str__(self):
        return f"{self.user} - ({self.status})"


class ReservationSeat(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    show_time = models.ForeignKey(ShowTime, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('seat', 'show_time')


class Payment(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(str(uuid.uuid4()))
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
