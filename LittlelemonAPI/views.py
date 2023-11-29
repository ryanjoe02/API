from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
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