from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import (
    AirplaneType,
    Airplane,
    Country,
    City,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
)

User = get_user_model()


def sample_image():
    return SimpleUploadedFile(
        name="test.jpg", content=b"file_content", content_type="image/jpeg"
    )


class BaseApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com", password="testpass123"
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

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
            image=sample_image(),
        )


class FlightViewSetTest(BaseApiTest):

    def test_list_flights(self):
        url = reverse("airport:flight-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_flight(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.flight.id)

    def test_filter_by_source_city(self):
        url = reverse("airport:flight-list")

        response = self.client.get(url, {"search": "New York"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AirplaneTypeViewSetTest(BaseApiTest):

    def test_list_airplane_types(self):
        url = reverse("airport:airplanetype-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_airplane_type(self):
        url = reverse("airport:airplanetype-list")

        payload = {"name": "Airbus A320"}

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AirplaneType.objects.filter(name="Airbus A320").exists())


class AirplaneViewSetTest(BaseApiTest):

    def test_list_airplanes(self):
        url = reverse("airport:airplane-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_image(self):
        url = reverse("airport:airplane-upload-image", args=[self.airplane.id])

        image = sample_image()

        response = self.client.post(url, {"image": image}, format="multipart")

        self.airplane.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.airplane.image)

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
            "country": self.country.id,
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
            "city": self.city1.id,
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

        payload = {"first_name": "Jane", "last_name": "Smith"}

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OrderViewSetTest(BaseApiTest):

    def test_list_orders_authenticated(self):
        self.client.force_authenticate(self.user)

        Order.objects.create(user=self.user)

        url = reverse("airport:order-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order_authenticated(self):
        self.client.force_authenticate(self.user)

        url = reverse("airport:order-list")

        payload = {"tickets": []}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
