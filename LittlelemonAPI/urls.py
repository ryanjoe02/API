from django.urls import path, include
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers

from .views import CategoryViewSet, MenuItemViewSet


router = routers.DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("menu-items", MenuItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]