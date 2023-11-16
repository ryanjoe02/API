from django.urls import path

from . import views

urlpatterns = [
    path("menu-items/", views.menu_item),
    path("menu-items/<int:pk>/", views.single_item),
]
