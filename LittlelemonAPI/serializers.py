from rest_framework import serializers
from decimal import Decimal

from .models import MenuItem, Category

# class MenuItemSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=10, decimal_places=2)
#     inventory = serializers.IntegerField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    # can change the field name
    stock = serializers.IntegerField(source="inventory")
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    # relationship with serializers
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField()

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "stock", "price_after_tax", "category"]

    def calculate_tax(self, product: MenuItem):
        return product.price * Decimal(1.1)
