from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
import io
from PIL import Image
from airport.models import (
    AirplaneType,
    Airplane,
    Country,
    City,
    Airport,
    Route,
    Flight,
    Crew,
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


class BaseApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_superuser(
            email="admin@test.com", password="admin123"
        )

        self.client.force_authenticate(self.user)

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

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
            image=sample_image(),
        )


class AirplaneTypeViewSetTest(BaseApiTest):
    def test_list_airplane_types(self):
        url = reverse("airport:airplane_type-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_airplane_type(self):
        url = reverse("airport:airplane_type-list")

        payload = {"name": "Airbus A320"}

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirplaneViewSetTest(BaseApiTest):
    def test_list_airplanes(self):
        url = reverse("airport:airplane-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_airplane(self):
        url = reverse("airport:airplane-list")

        payload = {
            "name": "Dreamliner",
            "rows": 30,
            "seats_in_row": 8,
            "airplane_type": self.airplane_type.id,
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_image(self):
        url = reverse("airport:airplane-upload-image", args=[self.airplane.id])

        response = self.client.post(url, {"image": sample_image()}, format="multipart")

        self.airplane.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.airplane.image)


class CountryViewSetTest(BaseApiTest):
    def test_list_countries(self):
        url = reverse("airport:country-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_country(self):
        url = reverse("airport:country-list")

        payload = {"name": "Germany"}

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CityViewSetTest(BaseApiTest):
    def test_list_cities(self):
        url = reverse("airport:city-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_city(self):
        url = reverse("airport:city-list")

        payload = {
            "name": "Berlin",
            "country_id": self.country.id,
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AirportViewSetTest(BaseApiTest):
    def test_list_airports(self):
        url = reverse("airport:airport-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_airport(self):
        url = reverse("airport:airport-list")

        payload = {
            "name": "LAX",
            "closest_big_city": "Los Angeles",
            "city_id": self.city1.id,
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RouteViewSetTest(BaseApiTest):
    def test_list_routes(self):
        url = reverse("airport:route-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_route(self):
        url = reverse("airport:route-detail", args=[self.route.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_route(self):
        airport3 = Airport.objects.create(
            name="SFO",
            closest_big_city="San Francisco",
            city=self.city1,
        )

        url = reverse("airport:route-list")

        payload = {
            "source": self.airport1.id,
            "destination": airport3.id,
            "distance": 2000,
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CrewViewSetTest(BaseApiTest):
    def test_list_crew(self):
        Crew.objects.create(first_name="John", last_name="Doe")

        url = reverse("airport:crew-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_crew(self):
        url = reverse("airport:crew-list")

        payload = {
            "first_name": "Jane",
            "last_name": "Smith",
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class FlightViewSetTest(BaseApiTest):
    def test_list_flights(self):
        url = reverse("airport:flight-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_flight(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderViewSetTest(BaseApiTest):
    def test_list_orders(self):
        Order.objects.create(user=self.user)

        url = reverse("airport:order-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        url = reverse("airport:order-list")

        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": self.flight.id,
                }
            ]
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
