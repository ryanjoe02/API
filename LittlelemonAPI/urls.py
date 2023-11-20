from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    # path("menu-items/", views.menu_item),
    # path("menu-items/<int:id>/", views.single_item),
    # only map the GET methods
    path("menu-items", views.MenuItemsViewSet.as_view({"get": "list"})),
    path("menu-items/<int:pk>", views.MenuItemsViewSet.as_view({"get": "retrieve"})),
    path("secret/", views.secret),
    # Only accept POST,
    path("api-token-auth/", obtain_auth_token),
    path("manager-view/", views.manager_view),
    path("throttle-check/", views.throttle_check),
    path("throttle-check-auth/", views.throttle_check_auth),
    path("groups/manager/users/", views.managers),
]
