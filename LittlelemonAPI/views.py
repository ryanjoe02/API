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
from django.contrib.auth.models import Group, User

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
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, throttle_classes


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


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def manager(request):
    managers = Group.objects.get(name="Manager")
    if request.method == "GET":
        users = [user.username for user in User.objects.filter(groups=managers).all()]
        return Response({"Managers": users})
    
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        if request.method == "POST":
            managers.user_set.add(user)
            user.is_staff = True
            user.save()
            return Response({"message": "Manager added successfully"}, status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            managers.user_set.remove(user)
            user.is_staff = False
            user.save()
            return Response({"message": "Manager removed successfully"}, status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def delivery_crew(request):
    delivery_crews = Group.objects.get(name="DeliveryCrew")
    if request.method == "GET":
        users = [user.username for user in User.objects.filter(groups=delivery_crew).all()]
        return Response({"Delivery Crews": users})
    
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        if request.method == "POST":
            delivery_crews.user_set.add(user)
            return Response({"message": "Delivery crew added successfully"}, status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            delivery_crews.user_set.remove(user)
            return Response({"message": "Delivery crew removed successfully"}, status.HTTP_200_OK)
    return Response({"message": "Invalid request"}, status.HTTP_400_BAD_REQUEST)
