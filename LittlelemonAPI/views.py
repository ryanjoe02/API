from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAdminUser,
    DjangoModelPermissions,
    DjangoModelPermissionsOrAnonReadOnly,
    IsAuthenticated,
)
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response


from .models import MenuItem, Category, Cart, Order
from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    UpdateCartSerializer,
    AddCartSerializer,
    CartSerializer,
    CreateOrderSerializer,
    UpdateOrderSerializer,
    OrderSerializer,
    SimpleOrderSerializer,
)
from .filters import MenuItemFilter, OrderFilter
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
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "featured", "category"]
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


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_class = OrderFilter
    search_fields = ["user__first_name", "orderitem__menuitem__title"]
    ordering_fields = ["total", "status", "date"]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [DjangoModelPermissions()]
        return [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        if user.groups.filter(name="DeliveryCrew").exists():
            return (
                (Order.objects.filter(delivery_crew=user.id))
                .select_related("user")
                .all()
            )
        return Order.objects.filter(user_id=user.id).select_related("user").all()

    def get_serializer_class(self):
        user = self.request.user

        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        else:
            if user.is_staff:
                return OrderSerializer
            return SimpleOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            date=request.data, context={"user_id": request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = SimpleOrderSerializer(order)
        return Response(serializer.data)
