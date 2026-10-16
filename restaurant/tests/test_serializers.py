from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from restaurant.models import Category, MenuItem, Booking, Cart
from restaurant.serializers import (
    BookingSerializer,
    MenuItemSerializer,
    CartSerializer,
    RegisterSerializer,
)


class BookingSerializerValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="booker", password="Password123")
        self.future_date = date.today() + timedelta(days=7)

    def test_valid_booking_serialization(self):
        data = {
            "name": "Jane Smith",
            "no_of_guests": 4,
            "booking_date": self.future_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 3,
            "special_requests": "Birthday celebration",
        }
        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_guests_zero(self):
        data = {
            "name": "Jane Smith",
            "no_of_guests": 0,
            "booking_date": self.future_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 3,
        }
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("no_of_guests", serializer.errors)

    def test_invalid_guests_exceed_limit(self):
        data = {
            "name": "Jane Smith",
            "no_of_guests": 25,
            "booking_date": self.future_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 3,
        }
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("no_of_guests", serializer.errors)

    def test_invalid_past_date(self):
        past_date = date.today() - timedelta(days=2)
        data = {
            "name": "Jane Smith",
            "no_of_guests": 2,
            "booking_date": past_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 3,
        }
        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("booking_date", serializer.errors)

    def test_conflict_validation_detects_existing_reservation(self):
        # Create an existing reservation
        Booking.objects.create(
            user=self.user,
            name="Existing Reservation",
            no_of_guests=2,
            booking_date=self.future_date,
            booking_time="19:00:00",
            table_number=4,
        )

        # Attempt to book the same table, date, and time
        duplicate_data = {
            "name": "Another Guest",
            "no_of_guests": 4,
            "booking_date": self.future_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 4,
        }
        serializer = BookingSerializer(data=duplicate_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class MenuItemSerializerValidationTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Drinks", slug="drinks")

    def test_valid_menu_item(self):
        data = {
            "title": "Lemonade",
            "price": "4.50",
            "category": self.category.id,
            "featured": False,
        }
        serializer = MenuItemSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_negative_price(self):
        data = {
            "title": "Lemonade",
            "price": "-2.00",
            "category": self.category.id,
        }
        serializer = MenuItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)


class CartSerializerValidationTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Sides", slug="sides")
        self.item = MenuItem.objects.create(title="Fries", price=Decimal("3.00"), category=self.category)

    def test_invalid_zero_quantity(self):
        serializer = CartSerializer(data={"menuitem": self.item.id, "quantity": 0})
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)


class RegisterSerializerTest(TestCase):
    def test_valid_registration(self):
        data = {"username": "newuser123", "password": "StrongPassword1", "email": "newuser@example.com"}
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password("StrongPassword1"))

    def test_duplicate_username_fails(self):
        User.objects.create_user(username="existinguser", password="Password123", email="exist@example.com")
        serializer = RegisterSerializer(data={"username": "existinguser", "password": "Password456", "email": "other@example.com"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
