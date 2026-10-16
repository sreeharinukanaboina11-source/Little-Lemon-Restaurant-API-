from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from restaurant.models import Category, MenuItem, Booking, Cart, Order, OrderItem


class StaticHtmlViewTest(APITestCase):
    """
    Coursera Capstone Requirement 1:
    Django serves static HTML content.
    """
    def test_static_html_home_rendered_at_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Little Lemon")
        self.assertContains(response, "Chicago")
        self.assertContains(response, "Mediterranean Kitchen")

    def test_static_html_home_rendered_at_restaurant_endpoint(self):
        response = self.client.get("/restaurant/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Little Lemon")


class AuthenticationApiTest(APITestCase):
    """
    Coursera Capstone Requirement 6:
    User registration and authentication work.
    """
    def test_user_registration_success(self):
        url = reverse("register")
        data = {
            "username": "tester1",
            "password": "SecurePassword123",
            "email": "tester1@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="tester1").exists())

    def test_obtain_auth_token_success(self):
        User.objects.create_user(username="tokenuser", password="Password123")
        url = reverse("api_token_auth")
        response = self.client.post(url, {"username": "tokenuser", "password": "Password123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_obtain_auth_token_invalid_credentials(self):
        url = reverse("api_token_auth")
        response = self.client.post(url, {"username": "nonexistent", "password": "WrongPassword"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MenuApiTest(APITestCase):
    """
    Coursera Capstone Requirement 4:
    Menu APIs are implemented correctly (list, retrieve, create, update, delete, permissions, search, filter).
    """
    def setUp(self):
        self.category = Category.objects.create(title="Mains", slug="mains")
        self.item1 = MenuItem.objects.create(title="Greek Salad", price=Decimal("12.50"), category=self.category)
        self.item2 = MenuItem.objects.create(title="Bruschetta", price=Decimal("8.00"), category=self.category)

        self.customer = User.objects.create_user(username="customer", password="Password123")
        self.customer_token = Token.objects.create(user=self.customer)

        self.manager = User.objects.create_user(username="manager", password="Password123")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        self.manager.groups.add(manager_group)
        self.manager_token = Token.objects.create(user=self.manager)

    def test_anonymous_user_can_list_menu_items(self):
        response = self.client.get("/api/menu-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_search_menu_items_by_title(self):
        response = self.client.get("/api/menu-items/?search=Greek")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Greek Salad")

    def test_filter_menu_items_by_category_slug(self):
        response = self.client.get("/api/menu-items/?category__slug=mains")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_customer_cannot_create_menu_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.customer_token.key}")
        data = {"title": "Lemon Dessert", "price": "6.00", "category": self.category.id}
        response = self.client.post("/api/menu-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_menu_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.manager_token.key}")
        data = {"title": "Lemon Dessert", "price": "6.00", "category": self.category.id, "featured": True}
        response = self.client.post("/api/menu-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Lemon Dessert")


class TableBookingApiTest(APITestCase):
    """
    Coursera Capstone Requirement 5:
    Table-booking APIs are implemented correctly.
    CRUD, date/time/table validation, prevention of overlapping reservations,
    and object-level customer authorization.
    """
    def setUp(self):
        self.user1 = User.objects.create_user(username="customer1", password="Password123")
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username="customer2", password="Password123")
        self.token2 = Token.objects.create(user=self.user2)

        self.manager = User.objects.create_user(username="manager1", password="Password123")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        self.manager.groups.add(manager_group)
        self.manager_token = Token.objects.create(user=self.manager)

        self.booking_date = date.today() + timedelta(days=5)

    def test_unauthenticated_cannot_access_bookings(self):
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_create_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        data = {
            "name": "Customer One",
            "no_of_guests": 4,
            "booking_date": self.booking_date.isoformat(),
            "booking_time": "19:00:00",
            "table_number": 2,
            "special_requests": "Window table",
        }
        response = self.client.post("/api/bookings/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Customer One")
        self.assertEqual(response.data["table_number"], 2)
        # Verify booking is attached to authenticated customer
        booking = Booking.objects.get(pk=response.data["id"])
        self.assertEqual(booking.user, self.user1)

    def test_customer_only_views_own_bookings(self):
        Booking.objects.create(
            user=self.user1,
            name="Booking Cust 1",
            no_of_guests=2,
            booking_date=self.booking_date,
            booking_time="18:00:00",
            table_number=1,
        )
        Booking.objects.create(
            user=self.user2,
            name="Booking Cust 2",
            no_of_guests=3,
            booking_date=self.booking_date,
            booking_time="18:00:00",
            table_number=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only contain user1's booking
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Booking Cust 1")

    def test_customer_cannot_modify_another_customer_booking(self):
        booking2 = Booking.objects.create(
            user=self.user2,
            name="Cust 2 Booking",
            no_of_guests=2,
            booking_date=self.booking_date,
            booking_time="18:00:00",
            table_number=1,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.patch(
            f"/api/bookings/{booking2.id}/",
            {"name": "Hijacked Booking"},
            format="json",
        )
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_overlapping_table_reservation_conflict_is_rejected(self):
        # Create first reservation for Table 5 at 20:00:00
        Booking.objects.create(
            user=self.user1,
            name="First Booking",
            no_of_guests=2,
            booking_date=self.booking_date,
            booking_time="20:00:00",
            table_number=5,
        )

        # Attempt second reservation for Table 5 at same date and time
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token2.key}")
        conflict_data = {
            "name": "Second Booker",
            "no_of_guests": 4,
            "booking_date": self.booking_date.isoformat(),
            "booking_time": "20:00:00",
            "table_number": 5,
        }
        response = self.client.post("/api/bookings/", conflict_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_manager_can_view_and_manage_all_bookings(self):
        Booking.objects.create(
            user=self.user1,
            name="Cust 1 Booking",
            no_of_guests=2,
            booking_date=self.booking_date,
            booking_time="18:00:00",
            table_number=1,
        )
        Booking.objects.create(
            user=self.user2,
            name="Cust 2 Booking",
            no_of_guests=4,
            booking_date=self.booking_date,
            booking_time="19:00:00",
            table_number=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.manager_token.key}")
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)


class RoleBasedAccessTest(APITestCase):
    """
    Tests for Manager and Delivery Crew role assignment and operations.
    """
    def setUp(self):
        self.admin = User.objects.create_superuser(username="adminuser", password="AdminPassword123", email="admin@example.com")
        self.admin_token = Token.objects.create(user=self.admin)

        self.manager = User.objects.create_user(username="mng1", password="Password123")
        mgr_group, _ = Group.objects.get_or_create(name="Manager")
        self.manager.groups.add(mgr_group)
        self.manager_token = Token.objects.create(user=self.manager)

        self.regular = User.objects.create_user(username="reg1", password="Password123")
        self.regular_token = Token.objects.create(user=self.regular)

    def test_admin_can_add_user_to_manager_group(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.post("/api/groups/manager/users/", {"username": "reg1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.regular.groups.filter(name="Manager").exists())

    def test_regular_user_cannot_modify_groups(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.regular_token.key}")
        response = self.client.post("/api/groups/manager/users/", {"username": "reg1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_add_user_to_delivery_crew(self):
        crew_user = User.objects.create_user(username="crewcandidate", password="Password123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.manager_token.key}")
        response = self.client.post("/api/groups/delivery-crew/users/", {"username": "crewcandidate"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(crew_user.groups.filter(name="Delivery crew").exists())


class CartAndOrderFlowTest(APITestCase):
    """
    Tests for Cart operations and Order placement/delivery pipeline.
    """
    def setUp(self):
        self.category = Category.objects.create(title="Pizzas", slug="pizzas")
        self.item = MenuItem.objects.create(title="Margherita", price=Decimal("14.00"), category=self.category)

        self.customer = User.objects.create_user(username="ordering_cust", password="Password123")
        self.customer_token = Token.objects.create(user=self.customer)

        self.crew = User.objects.create_user(username="crewguy", password="Password123")
        crew_group, _ = Group.objects.get_or_create(name="Delivery crew")
        self.crew.groups.add(crew_group)
        self.crew_token = Token.objects.create(user=self.crew)

    def test_customer_cart_and_checkout_flow(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.customer_token.key}")

        # 1. Add to cart
        cart_resp = self.client.post("/api/cart/menu-items/", {"menuitem": self.item.id, "quantity": 2}, format="json")
        self.assertEqual(cart_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cart_resp.data["quantity"], 2)

        # 2. View cart
        view_resp = self.client.get("/api/cart/menu-items/")
        self.assertEqual(view_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(view_resp.data), 1)

        # 3. Checkout (create order)
        order_resp = self.client.post("/api/orders/")
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(str(order_resp.data["total"])), Decimal("28.00"))

        # 4. Cart should now be empty
        empty_cart_resp = self.client.get("/api/cart/menu-items/")
        self.assertEqual(len(empty_cart_resp.data), 0)

    def test_delivery_crew_can_update_assigned_order_status(self):
        order = Order.objects.create(user=self.customer, delivery_crew=self.crew, total=Decimal("28.00"))
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.crew_token.key}")

        response = self.client.patch(f"/api/orders/{order.id}/", {"status": "delivered"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")
