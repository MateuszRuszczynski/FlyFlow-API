from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
import io
from PIL import Image

from airport import serializers
from airport.models import (
    AirplaneType,
    Airplane,
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order,
)

User = get_user_model()


def sample_image():
    file_str = io.BytesIO()
    image = Image.new("RGB", (10, 10), "white")
    image.save(file_str, format="JPEG")
    file_str.seek(0)
    return SimpleUploadedFile(
        name="test.jpg", content=file_str.read(), content_type="image/jpeg"
    )


class SerializerTestMixin(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="password123"
        )

        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")

        self.airplane = Airplane.objects.create(
            name="B737",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        self.country = Country.objects.create(name="USA")

        self.city1 = City.objects.create(name="New York", country=self.country)

        self.city2 = City.objects.create(name="Chicago", country=self.country)

        self.airport1 = Airport.objects.create(
            name="JFK",
            closest_big_city="New York",
            city=self.city1,
        )

        self.airport2 = Airport.objects.create(
            name="ORD",
            closest_big_city="Chicago",
            city=self.city2,
        )

        self.route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=1200,
        )

        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
            image=sample_image(),
        )

        self.flight.crew.add(self.crew)

        self.order = Order.objects.create(user=self.user)

        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order,
        )


class AirplaneTypeSerializerTest(SerializerTestMixin):
    def test_serializer(self):
        serializer = serializers.AirplaneTypeSerializer(self.airplane_type)

        self.assertEqual(
            serializer.data,
            {
                "id": self.airplane_type.id,
                "name": "Boeing 737",
            },
        )


class AirplaneSerializerTest(SerializerTestMixin):
    def test_airplane_serializer(self):
        serializer = serializers.AirplaneSerializer(self.airplane)

        self.assertEqual(serializer.data["name"], self.airplane.name)

    def test_airplane_list_serializer(self):
        serializer = serializers.AirplaneListSerializer(self.airplane)

        self.assertEqual(serializer.data["total_places"], 120)

        self.assertEqual(serializer.data["airplane_type"], "Boeing 737")


class CountrySerializerTest(SerializerTestMixin):
    def test_country_serializer(self):
        serializer = serializers.CountrySerializer(self.country)

        self.assertEqual(serializer.data["name"], "USA")


class CitySerializerTest(SerializerTestMixin):
    def test_city_serializer(self):
        serializer = serializers.CitySerializer(self.city1)

        self.assertEqual(serializer.data["name"], "New York")

        self.assertEqual(serializer.data["country"]["name"], "USA")


class AirportSerializerTest(SerializerTestMixin):
    def test_airport_serializer(self):
        serializer = serializers.AirportSerializer(self.airport1)

        self.assertEqual(serializer.data["name"], "JFK")

        self.assertEqual(serializer.data["city"], str(self.city1))


class RouteSerializerTest(SerializerTestMixin):
    def test_route_serializer(self):
        serializer = serializers.RouteSerializer(self.route)

        self.assertEqual(serializer.data["distance"], 1200)

    def test_route_list_serializer(self):
        serializer = serializers.RouteListSerializer(self.route)

        self.assertEqual(serializer.data["source"], "JFK")

        self.assertEqual(serializer.data["destination"], "ORD")

    def test_route_detail_serializer(self):
        serializer = serializers.RouteDetailSerializer(self.route)

        self.assertEqual(serializer.data["source"]["name"], "JFK")

        self.assertEqual(serializer.data["destination"]["name"], "ORD")


class CrewSerializerTest(SerializerTestMixin):
    def test_crew_serializer(self):
        serializer = serializers.CrewSerializer(self.crew)

        self.assertEqual(serializer.data["first_name"], "John")


class FlightSerializerTest(SerializerTestMixin):
    def test_flight_serializer(self):
        serializer = serializers.FlightSerializer(self.flight)

        self.assertEqual(serializer.data["airplane"], self.airplane.id)

    def test_flight_list_serializer(self):
        serializer = serializers.FlightListSerializer(self.flight)

        self.assertEqual(serializer.data["airplane_name"], "B737")

        self.assertEqual(serializer.data["airplane_capacity"], 120)

    def test_flight_detail_serializer(self):
        serializer = serializers.FlightDetailSerializer(self.flight)

        self.assertEqual(serializer.data["route"]["source"]["name"], "JFK")

        self.assertEqual(serializer.data["airplane"]["name"], "B737")

        self.assertEqual(len(serializer.data["crew"]), 1)

    def test_flight_serializer_invalid_time(self):
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() - timedelta(hours=1),
            "crew": [],
        }

        serializer = serializers.FlightSerializer(data=data)

        self.assertFalse(serializer.is_valid())


class TicketSerializerTest(SerializerTestMixin):
    def test_ticket_serializer(self):
        serializer = serializers.TicketSerializer(self.ticket)

        self.assertEqual(serializer.data["row"], 1)

        self.assertEqual(serializer.data["seat"], 1)

    def test_ticket_invalid_row(self):
        data = {
            "row": 100,
            "seat": 1,
            "flight": self.flight.id,
        }

        serializer = serializers.TicketSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_ticket_invalid_seat(self):
        data = {
            "row": 1,
            "seat": 100,
            "flight": self.flight.id,
        }

        serializer = serializers.TicketSerializer(data=data)

        self.assertFalse(serializer.is_valid())


class OrderSerializerTest(SerializerTestMixin):
    def test_order_serializer(self):
        serializer = serializers.OrderSerializer(self.order)

        self.assertEqual(serializer.data["id"], self.order.id)

    def test_order_list_serializer(self):
        serializer = serializers.OrderListSerializer(self.order)

        self.assertEqual(serializer.data["user"], self.user.email)

    def test_create_order_with_tickets(self):
        data = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 2,
                    "flight": self.flight.id,
                }
            ]
        }

        serializer = serializers.OrderSerializer(
            data=data, context={"request": type("Request", (), {"user": self.user})()}
        )

        self.assertTrue(serializer.is_valid())

        order = serializer.save()

        self.assertEqual(order.tickets.count(), 1)
