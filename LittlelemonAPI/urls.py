from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path(
        "menu-items/", views.MenuItemViewSet.as_view({"get": "list", "post": "create"})
    ),
    path(
        "menu-items/<int:pk>/",
        views.SingleMenuItemViewSet.as_view(),
        name="single-menu-item",
    ),
]
