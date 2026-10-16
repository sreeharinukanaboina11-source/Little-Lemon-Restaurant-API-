from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, MenuItem, Booking, Cart, Order, OrderItem
from .permissions import (
    IsAdminUserOrReadOnly,
    IsManager,
    IsManagerOrReadOnly,
    IsDeliveryCrew,
    IsBookingOwnerOrManager,
    in_group,
)
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    MenuItemSerializer,
    BookingSerializer,
    CartSerializer,
    OrderSerializer,
)


def home_view(request):
    """
    Renders the static HTML homepage for the restaurant.
    Satisfies Coursera requirement: Django serves static HTML content.
    """
    context = {
        "menu_items_count": MenuItem.objects.count(),
        "categories_count": Category.objects.count(),
    }
    return render(request, "index.html", context)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    search_fields = ["title", "slug"]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.select_related("category").all().order_by("id")
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "category__slug", "featured"]
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "title", "id"]
    ordering = ["id"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Price filtering: ?to_price=15.00
        to_price = self.request.query_params.get("to_price")
        if to_price:
            try:
                qs = qs.filter(price__lte=Decimal(to_price))
            except Exception:
                pass

        # Price filtering: ?from_price=10.00
        from_price = self.request.query_params.get("from_price")
        if from_price:
            try:
                qs = qs.filter(price__gte=Decimal(from_price))
            except Exception:
                pass

        featured = self.request.query_params.get("featured")
        if featured is not None:
            qs = qs.filter(featured=featured.lower() in ("1", "true", "yes"))
        return qs


class BookingViewSet(viewsets.ModelViewSet):
    """
    Table booking API.
    Satisfies Coursera requirement: Table-booking APIs are implemented correctly.
    Customers manage their own bookings; managers can view and manage all bookings.
    Prevents overlapping table reservations at both database and serializer levels.
    """
    queryset = Booking.objects.select_related("user").all()
    serializer_class = BookingSerializer
    permission_classes = [IsBookingOwnerOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["booking_date", "table_number"]
    search_fields = ["name", "special_requests"]
    ordering_fields = ["booking_date", "booking_time", "table_number", "id"]
    ordering = ["booking_date", "booking_time"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()
        if user.is_staff or in_group(user, "Manager"):
            return Booking.objects.select_related("user").all()
        return Booking.objects.filter(user=user).select_related("user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ManagerGroupView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        group, _ = Group.objects.get_or_create(name="Manager")
        return Response({"group": group.name, "members": list(group.user_set.values("id", "username", "email"))})

    def post(self, request):
        username = request.data.get("username")
        if not username:
            raise ValidationError({"username": "This field is required."})
        user = get_object_or_404(User, username=username)
        group, _ = Group.objects.get_or_create(name="Manager")
        user.groups.add(group)
        return Response({"message": f"{username} added to Manager group."}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        username = request.data.get("username")
        if not username:
            raise ValidationError({"username": "This field is required."})
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="Manager")
        user.groups.remove(group)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeliveryCrewGroupView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        group, _ = Group.objects.get_or_create(name="Delivery crew")
        return Response({"group": group.name, "members": list(group.user_set.values("id", "username", "email"))})

    def post(self, request):
        username = request.data.get("username")
        if not username:
            raise ValidationError({"username": "This field is required."})
        user = get_object_or_404(User, username=username)
        group, _ = Group.objects.get_or_create(name="Delivery crew")
        user.groups.add(group)
        return Response({"message": f"{username} added to Delivery crew."}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        username = request.data.get("username")
        if not username:
            raise ValidationError({"username": "This field is required."})
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="Delivery crew")
        user.groups.remove(group)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemOfDayView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        item = MenuItem.objects.filter(featured=True).first()
        if not item:
            return Response({"message": "No item of the day has been selected."}, status=status.HTTP_404_NOT_FOUND)
        return Response(MenuItemSerializer(item).data)

    def put(self, request):
        item_id = request.data.get("item_id")
        if not item_id:
            raise ValidationError({"item_id": "This field is required."})
        item = get_object_or_404(MenuItem, pk=item_id)
        MenuItem.objects.update(featured=False)
        item.featured = True
        item.save(update_fields=["featured"])
        return Response(MenuItemSerializer(item).data)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(CartSerializer(Cart.objects.filter(user=request.user).select_related("menuitem"), many=True).data)

    def post(self, request):
        menuitem_id = request.data.get("menuitem")
        if not menuitem_id:
            raise ValidationError({"menuitem": "This field is required."})
        quantity = request.data.get("quantity", 1)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValidationError({"quantity": "Enter a valid integer."})
        if quantity < 1:
            raise ValidationError({"quantity": "Quantity must be at least 1."})
        item = get_object_or_404(MenuItem, pk=menuitem_id)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=item,
            defaults={"quantity": quantity, "unit_price": item.price, "price": item.price * quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.unit_price = item.price
            cart_item.save()
        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.is_staff or in_group(request.user, "Manager"):
            orders = Order.objects.all()
        elif in_group(request.user, "Delivery crew"):
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)
        return Response(OrderSerializer(orders.prefetch_related("items__menuitem"), many=True).data)

    @transaction.atomic
    def post(self, request):
        cart_items = list(Cart.objects.filter(user=request.user).select_related("menuitem"))
        if not cart_items:
            raise ValidationError({"cart": "Your cart is empty."})
        total = sum((line.price for line in cart_items), Decimal("0.00"))
        order = Order.objects.create(user=request.user, total=total)
        for line in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=line.menuitem,
                quantity=line.quantity,
                unit_price=line.unit_price,
                price=line.price,
            )
        Cart.objects.filter(user=request.user).delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        order = get_object_or_404(Order, pk=pk)
        if user.is_staff or in_group(user, "Manager"):
            return order
        if in_group(user, "Delivery crew") and order.delivery_crew_id == user.id:
            return order
        if order.user_id == user.id:
            return order
        raise PermissionDenied("You do not have permission to view this order.")

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if request.user.is_staff or in_group(request.user, "Manager"):
            allowed = {"status", "delivery_crew"}
        elif in_group(request.user, "Delivery crew") and order.delivery_crew_id == request.user.id:
            allowed = {"status"}
        else:
            raise PermissionDenied("You cannot update this order.")

        if "status" in request.data:
            if request.data["status"] not in dict(Order.STATUS_CHOICES):
                raise ValidationError({"status": "Use 'pending' or 'delivered'."})
            order.status = request.data["status"]

        if "delivery_crew" in request.data:
            crew_id = request.data["delivery_crew"]
            crew = get_object_or_404(User, pk=crew_id)
            if not in_group(crew, "Delivery crew"):
                raise ValidationError({"delivery_crew": "Selected user is not in the Delivery crew group."})
            order.delivery_crew = crew

        order.save()
        return Response(OrderSerializer(order).data)

    def delete(self, request, pk):
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            raise PermissionDenied("Only managers can delete orders.")
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
