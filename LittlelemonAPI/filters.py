from django_filters.rest_framework import FilterSet, DjangoFilterBackend

from .models import MenuItem, Order


class MenuItemFilter(FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            "title": ["exact", "contains"],
            "price": ["gte", "lte"],
            "category_id": ["exact"],
        }


class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            "user_id": ["exact"],
            "delivery_crew_id": ["exact"],
            "status": ["exact"],
            "total": ["gte", "lte"],
            "date": ["year__gte", "year__lte"],
        }


class CustomDjangoFilterBackend(DjangoFilterBackend):
    def to_html(self, request, queryset, view):
        return None
