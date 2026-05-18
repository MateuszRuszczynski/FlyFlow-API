from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from users.serializers import (
    RegisterSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterSerializerTests(APITestCase):
    def test_register_serializer_valid(self):
        data = {
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_register_serializer_password_mismatch(self):
        data = {
            "email": "user@example.com",
            "password": "StrongPass123!",
            "password_confirm": "WrongPassword123!",
        }

        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class ChangePasswordSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="OldPassword123!",
        )

    def test_change_password_serializer_valid(self):
        self.client.force_authenticate(user=self.user)

        serializer = ChangePasswordSerializer(
            data={
                "old_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "new_password_confirm": "NewPassword123!",
            },
            context={"request": self.client.request()},
        )

        serializer.context["request"].user = self.user

        self.assertTrue(serializer.is_valid())

    def test_change_password_wrong_old_password(self):
        serializer = ChangePasswordSerializer(
            data={
                "old_password": "WrongPassword",
                "new_password": "NewPassword123!",
                "new_password_confirm": "NewPassword123!",
            },
            context={"request": type("Request", (), {"user": self.user})()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_change_password_mismatch(self):
        serializer = ChangePasswordSerializer(
            data={
                "old_password": "OldPassword123!",
                "new_password": "NewPassword123!",
                "new_password_confirm": "WrongPassword123!",
            },
            context={"request": type("Request", (), {"user": self.user})()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
