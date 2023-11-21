from django.contrib import admin
from django.urls import path, include

from .views import MenuItemListView

urlpatterns = [path("menu-items/", MenuItemListView.as_view())]
