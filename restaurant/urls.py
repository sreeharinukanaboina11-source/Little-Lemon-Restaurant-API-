from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    CategoryViewSet,
    MenuItemViewSet,
    BookingViewSet,
    ManagerGroupView,
    DeliveryCrewGroupView,
    ItemOfDayView,
    CartView,
    OrderView,
    OrderDetailView,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"menu-items", MenuItemViewSet, basename="menu-item")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"booking/tables", BookingViewSet, basename="booking-table")
router.register(r"tables", BookingViewSet, basename="table")

urlpatterns = [
    path("", include(router.urls)),
    path("users/", RegisterView.as_view(), name="register"),
    path("groups/manager/users/", ManagerGroupView.as_view(), name="manager-users"),
    path("groups/delivery-crew/users/", DeliveryCrewGroupView.as_view(), name="delivery-crew-users"),
    path("menu-items-of-the-day/", ItemOfDayView.as_view(), name="item-of-the-day"),
    path("cart/menu-items/", CartView.as_view(), name="cart"),
    path("orders/", OrderView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
