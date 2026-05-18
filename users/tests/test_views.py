from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthViewsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
        )

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return refresh

    def test_register_view(self):
        url = reverse("user:register")

        data = {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_me_view_get(self):
        self.authenticate()

        url = reverse("user:me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_me_view_update(self):
        self.authenticate()

        url = reverse("user:me")
        response = self.client.patch(
            url,
            {"first_name": "Updated"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_change_password(self):
        self.authenticate()

        url = reverse("user:change-password")

        data = {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass123!",
            "new_password_confirm": "NewStrongPass123!",
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass123!"))

    def test_logout_view(self):
        refresh = self.authenticate()

        url = reverse("user:logout")

        response = self.client.post(
            url,
            {"refresh": str(refresh)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_token(self):
        self.authenticate()

        url = reverse("user:logout")

        response = self.client.post(
            url,
            {"refresh": "invalid_token"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
