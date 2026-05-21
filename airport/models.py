from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint, CheckConstraint, Q, F
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import os
import uuid


class AirplaneType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def validate_image_size(file):
    max_size = 2 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Image file too large. Size should not exceed 2MB")


def airplane_image_file_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    return os.path.join("upload/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=50)
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.IntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.PROTECT, related_name="airplanes"
    )
    image = models.ImageField(
        null=True, upload_to=airplane_image_file_path, validators=[validate_image_size]
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            CheckConstraint(condition=Q(rows__gt=0), name="rows_positive"),
            CheckConstraint(condition=Q(seats_in_row__gt=0), name="seats_positive"),
        ]

    @property
    def total_places(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} {self.airplane_type}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} at {self.created_at:%Y-%m-%d}"


class Country(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="cities"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}, {self.country}"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="airports")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.city}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.PROTECT, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.PROTECT, related_name="routes_to"
    )
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["source", "destination"]
        constraints = [
            UniqueConstraint(fields=["source", "destination"], name="unique_route"),
            CheckConstraint(
                condition=~Q(source=F("destination")),
                name="source_destination_cannot_be_equal",
            ),
        ]

    def __str__(self):
        return f"{self.source} - {self.destination}, {self.distance}km"


class Crew(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["departure_time"]
        constraints = [
            CheckConstraint(
                condition=Q(arrival_time__gt=F("departure_time")),
                name="arrival_time_must_be_after_departure",
            )
        ]

    def __str__(self):
        return (
            f"{self.route} | "
            f"{self.departure_time.strftime('%Y-%m-%d %H:%M')} → "
            f"{self.arrival_time.strftime('%Y-%m-%d %H:%M')}"
        )

    def clean(self):
        if self.departure_time and self.arrival_time:
            if self.arrival_time <= self.departure_time:
                raise ValidationError(
                    {"arrival_time": "Arrival time must be later than departure time."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Ticket(models.Model):
    row = models.IntegerField(validators=[MinValueValidator(1)])
    seat = models.IntegerField(validators=[MinValueValidator(1)])
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        ordering = ["row", "seat"]
        constraints = [
            UniqueConstraint(fields=["flight", "row", "seat"], name="unique_ticket"),
            CheckConstraint(condition=Q(row__gt=0), name="ticket_row_positive"),
            CheckConstraint(condition=Q(seat__gt=0), name="ticket_seat_positive"),
        ]

    def __str__(self):
        return f"Row: {self.row}, seat: {self.seat} | {self.flight}"

    def clean(self):
        if not self.flight or not hasattr(self.flight, "airplane"):
            return

        airplane = self.flight.airplane
        errors = {}

        if self.row and not (1 <= self.row <= airplane.rows):
            errors["row"] = f"Row must be in range [1-{airplane.rows}]"
        if self.seat and not (1 <= self.seat <= airplane.seats_in_row):
            errors["seat"] = f"Seat must be in range [1-{airplane.seats_in_row}]"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
