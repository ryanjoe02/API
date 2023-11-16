from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import MenuItem
from .serializers import MenuItemSerializer


# /api/menu-item/ : display the menu items that you've set in serializers.py as JSON data

@api_view(['GET', 'POST'])
def menu_item(request):
    items = MenuItem.objects.select_related("category").all()
    serialized_item = MenuItemSerializer(items, many=True)
    return Response(serialized_item.data)

@api_view(['GET', 'POST'])
def single_item(request):
    items = get_object_or_404(MenuItem, pk=id)
    serialized_item = MenuItemSerializer(items)
    return Response(serialized_item.data)
