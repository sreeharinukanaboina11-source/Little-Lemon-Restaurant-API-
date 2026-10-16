from datetime import date
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, MenuItem, Booking, Cart, Order, OrderItem


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "first_name", "last_name"]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_name"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "user_username",
            "name",
            "no_of_guests",
            "booking_date",
            "booking_time",
            "table_number",
            "special_requests",
            "created_at",
        ]
        read_only_fields = ["user", "created_at"]

    def validate_no_of_guests(self, value):
        if value < 1:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        if value > 20:
            raise serializers.ValidationError("Online reservations accept up to 20 guests. Please call for large events.")
        return value

    def validate_table_number(self, value):
        if value < 1 or value > 30:
            raise serializers.ValidationError("Table number must be between 1 and 30.")
        return value

    def validate_booking_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Booking date cannot be in the past.")
        return value

    def validate(self, attrs):
        # Check conflict on table_number, booking_date, booking_time
        table_number = attrs.get("table_number", self.instance.table_number if self.instance else 1)
        booking_date = attrs.get("booking_date", self.instance.booking_date if self.instance else None)
        booking_time = attrs.get("booking_time", self.instance.booking_time if self.instance else "18:00:00")

        if booking_date:
            conflict_qs = Booking.objects.filter(
                table_number=table_number,
                booking_date=booking_date,
                booking_time=booking_time,
            )
            if self.instance:
                conflict_qs = conflict_qs.exclude(pk=self.instance.pk)

            if conflict_qs.exists():
                raise serializers.ValidationError(
                    {"non_field_errors": [f"Table {table_number} is already reserved for {booking_date} at {booking_time}."]}
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source="menuitem.title", read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "menuitem", "menuitem_title", "quantity", "unit_price", "price"]
        read_only_fields = ["unit_price", "price"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_title = serializers.CharField(source="menuitem.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menuitem", "menuitem_title", "quantity", "unit_price", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "username", "delivery_crew", "status", "total", "date", "items"]
        read_only_fields = ["user", "total", "date", "items"]
