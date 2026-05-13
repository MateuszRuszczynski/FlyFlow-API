from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.utils import IntegrityError
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from airport.models import (
    AirplaneType,
    Airplane,
    Order,
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
)


def get_test_image():
    return SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")


class AirlineModelsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        self.airplane_type = AirplaneType.objects.create(name="Airbus A320")
        self.airplane = Airplane.objects.create(
            name="A320-Neo", rows=20, seats_in_row=6, airplane_type=self.airplane_type
        )
        self.country = Country.objects.create(name="Germany")
        self.city = City.objects.create(name="Berlin", country=self.country)
        self.airport_src = Airport.objects.create(
            name="TXL", closest_big_city="Berlin", city=self.city
        )
        self.airport_dst = Airport.objects.create(
            name="MUC", closest_big_city="Munich", city=self.city
        )
        self.route = Route.objects.create(
            source=self.airport_src, destination=self.airport_dst, distance=500
        )

    def test_airplane_total_places(self):
        self.assertEqual(self.airplane.total_places, 120)

    def test_route_source_and_destination_cannot_be_equal(self):
        with self.assertRaises(IntegrityError):
            Route.objects.create(
                source=self.airport_src, destination=self.airport_src, distance=100
            )

    def test_flight_time_validation(self):
        now = timezone.now()
        flight = Flight(
            route=self.route,
            airplane=self.airplane,
            departure_time=now,
            arrival_time=now - timedelta(hours=2),
        )
        with self.assertRaises(ValidationError):
            flight.clean()

    def test_ticket_clean_invalid_row(self):
        now = timezone.now()
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=now,
            arrival_time=now + timedelta(hours=1),
            image=get_test_image()
        )
        order = Order.objects.create(user=self.user)
        ticket = Ticket(row=25, seat=1, flight=flight, order=order)

        with self.assertRaises(ValidationError) as error:
            ticket.clean()

        self.assertIn("row", error.exception.message_dict)
