from datetime import date, time
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from restaurant.models import Category, MenuItem, Booking, Cart, Order, OrderItem


class MenuItemModelTest(TestCase):
    """
    Tests for MenuItem model.
    Coursera Capstone test requirement: test string representation and fields.
    """
    def setUp(self):
        self.category = Category.objects.create(title="Desserts", slug="desserts")

    def test_create_menu_item(self):
        item = MenuItem.objects.create(
            title="IceCream",
            price=Decimal("80.00"),
            category=self.category,
            featured=True,
        )
        self.assertEqual(item.title, "IceCream")
        self.assertEqual(item.price, Decimal("80.00"))
        self.assertTrue(item.featured)
        self.assertEqual(str(item), "IceCream : 80.00")

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), "Desserts")


class BookingModelTest(TestCase):
    """
    Tests for Booking model.
    Coursera Capstone test requirement: test table reservation creation and constraints.
    """
    def setUp(self):
        self.user = User.objects.create_user(username="johndoe", password="Password123")

    def test_create_booking_success(self):
        booking = Booking.objects.create(
            user=self.user,
            name="John Doe",
            no_of_guests=4,
            booking_date=date(2026, 12, 25),
            booking_time=time(19, 0),
            table_number=5,
            special_requests="Window seat please",
        )
        self.assertEqual(booking.name, "John Doe")
        self.assertEqual(booking.no_of_guests, 4)
        self.assertEqual(booking.table_number, 5)
        self.assertIn("Booking", str(booking))
        self.assertIn("Table 5", str(booking))

    def test_booking_duplicate_slot_constraint(self):
        """Database constraint should prevent duplicate booking for same table and time."""
        Booking.objects.create(
            user=self.user,
            name="John Doe",
            no_of_guests=2,
            booking_date=date(2026, 12, 25),
            booking_time=time(19, 0),
            table_number=5,
        )
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                user=self.user,
                name="Another Person",
                no_of_guests=3,
                booking_date=date(2026, 12, 25),
                booking_time=time(19, 0),
                table_number=5,
            )


class OrderAndCartModelTest(TestCase):
    """
    Tests for Cart and Order models.
    """
    def setUp(self):
        self.user = User.objects.create_user(username="cartuser", password="Password123")
        self.category = Category.objects.create(title="Main", slug="main")
        self.menu_item = MenuItem.objects.create(
            title="Pasta",
            price=Decimal("15.50"),
            category=self.category,
        )

    def test_cart_auto_calculates_price(self):
        cart = Cart.objects.create(
            user=self.user,
            menuitem=self.menu_item,
            quantity=3,
            unit_price=self.menu_item.price,
            price=Decimal("0.00"),
        )
        self.assertEqual(cart.price, Decimal("46.50"))

    def test_order_creation_and_string(self):
        order = Order.objects.create(user=self.user, total=Decimal("46.50"))
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertIn("Order #", str(order))
