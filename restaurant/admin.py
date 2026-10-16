from django.contrib import admin
from .models import Category, MenuItem, Booking, Cart, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "category", "featured")
    list_filter = ("category", "featured")
    search_fields = ("title",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "no_of_guests", "booking_date", "booking_time", "table_number", "user")
    list_filter = ("booking_date", "table_number")
    search_fields = ("name", "special_requests")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "delivery_crew", "status", "total", "date")
    list_filter = ("status",)
    inlines = [OrderItemInline]


admin.site.register(Cart)
