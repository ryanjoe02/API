from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group

from .models import MenuItem
from .serializers import MenuItemSerializer
from .throttles import TenCallsPerMinute


# /api/menu-item/ : display the menu items that you've set in serializers.py as JSON data
@api_view(["GET", "POST"])
def menu_item(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__istartwith=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        # Pagination
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    if request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def single_item(request, id):
    item = get_object_or_404(MenuItem, pk=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)


# Class-Based views
class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    # Ordering & Sorting
    ordering_fields = ["price", "inventory"]
    # Search field field name = title , category = title
    search_fields = ["title", "category__title"]
    # throttling for CBVs, Endpoints will be throttled for both anon and authenticated user
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_throttles(self):
        if self.action == "create":
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = []
        return [throttle_classes() for throttle in throttle_classes]


@api_view()
@permission_classes([IsAuthenticated])  # Secret message only for authenticated user
def secret(request):
    return Response({"message": "Some secret message"})


@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only Manager Should See This"})
    else:
        return Response({"message": "You are not Manager"}, status.HTTP_403_FORBIDDEN)


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response({"message": "message for the logged in user only"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == "POST":
            managers.user_set.add(user)
        elif request.method == "DELETE":
            managers.user_set.remove(user)

        return Response({"message": "ok"})

    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
