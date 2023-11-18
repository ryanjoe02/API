from django.urls import path

from . import views

urlpatterns = [
    # path("menu-items/", views.menu_item),
    # path("menu-items/<int:id>/", views.single_item),

    # only map the GET methods
    path('menu-items',views.MenuItemsViewSet.as_view({'get':'list'})),
    path('menu-items/<int:pk>',views.MenuItemsViewSet.as_view({'get':'retrieve'})),
]
