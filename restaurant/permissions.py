from rest_framework.permissions import BasePermission, SAFE_METHODS


def in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or in_group(request.user, "Manager"))
        )


class IsManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or in_group(request.user, "Manager"))
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or in_group(request.user, "Delivery crew"))
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsBookingOwnerOrManager(BasePermission):
    """
    Object-level permission allowing users to manage only their own bookings,
    while managers and staff can view and manage all bookings.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or in_group(request.user, "Manager"):
            return True
        return obj.user == request.user
