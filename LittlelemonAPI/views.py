from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MenuItem, Category, Cart
from .serializers import MenuItemSerializer, CategorySerializer, UpdateCartSerializer, AddCartSerializer, CartSerializer
from .filters import MenuItemFilter
from .paginations import MenuItemPagnation




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser, DjangoModelPermissions]
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuItemFilter
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', "featured", "category"]
    pagination_class = MenuItemPagnation
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]


class CartViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartSerializer
        elif self.request.method == "PATCH":
            return UpdateCartSerializer
        return CartSerializer

    def get_serializer_context(self):
        return {"user_id": self.request.user.id}

    def get_queryset(self):
        user = self.request.user.id

        try:
            return Cart.objects.filter(user_id=user).select_related("menuitem").all()
        except Cart.DoesNotExist:
            return Cart.objects.create(user_id=user)
    
