from rest_framework import viewsets, permissions, generics

from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework.response import Response


# /menu-items
class CustomerReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name="Customer").exists()
        return False


class DeliveryReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name="DeliveryCrew").exists()
        return False


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_field = ["price"]

    def get_permissions(self):
        user = self.request.user

        if user.groups.filter(name="Manager").exists():
            permission_classes = [permissions.AllowAny]
        elif user.groups.filter(name="Customer").exists():
            permission_classes = [CustomerReadOnly]
        elif user.groups.filter(name="DeliveryCrew").exists():
            permission_classes = [DeliveryReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class SingleMenuItemViewSet(generics.RetrieveAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = "pk"
