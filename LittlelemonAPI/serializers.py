from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction

from .models import MenuItem, Category, Cart, OrderItem, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "featured",
            "category",
        ]


class SimpleMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
        ]

class CartSerializer(serializers.ModelSerializer):
    menuitem = SimpleMenuItemSerializer()
    price = serializers.SerializerMethodField()

    def get_price(self, cart: Cart):
        return cart.quantity * cart.menuitem.price
    class Meta:
        model = Cart
        fields = [
            "id",
            "menuitem",
            "quantity",
            "price",
        ]


class AddCartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField()

    def validate_id(self, value):
        try:
            MenuItem.objects.get(id=value)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Invalid menu item id")
        return value
    
    def save(self):
        user_id = self.context["user_id"]
        menuitem_id = self.validated_data["menuitem_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = Cart.objects.get(user_id=user_id, menuitem_id=menuitem_id)
            cart_item.quantity = quantity
            cart_item.save()
            self.instance = cart_item
        except Cart.DoesNotExist:
            self.instance = Cart.objects.create(user_id=user_id, **self.validated_data)
        return self.instance
    
    class Meta:
        model = Cart
        fields = [
            "id", "menuitem_id", "quantity"
        ]


class UpdateCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id", "quantity"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = SimpleMenuItemSerializer()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menuitem",
            "quantity",
            "unit_price",
            "price"
        ]


class UserSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, user: User):
        return f"{user.first_name} {user.last_name}"
    
    class Meta:
        model = User
        fields = [
            "user_name"
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    def get_total(self, order: Order):
        return sum([item.quantity * item.menuitem.price for item in order.items.all()])


    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_crew",
            "status",
            "items",
            "total",
            "date",
        ]

class SimpleOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()

    def get_order_status(self, order: Order):
        if not order.status and not order.delivery_crew:
            return "Order is not yet sent"
        if not order.status and order.delivery_crew:
            return "Delivery crew is on the way"
        if order.status and order.delivery_crew:
            return "Order is delivered"
        
    def get_total(self, order: Order):
        return sum([item.quantity * item.menuitem.price for item in order.items.all()])
    
    class Meta:
        model = Order
        fields = ["id", "user", "order_status", "items", "total", "date"]


class CreateOrderSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(read_only=True)

    def save(self):
        user = self.context["user_id"]

        if not Cart.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("No Cart")
        with transaction.atomic():
            order = Order.objects.create(user_id=user)
            cart_items = Cart.objects.select_related("menuitem").filter(user_id=user)

            order_items = [
                OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    unit_price=item.menuitem.price,
                    quantity=item.quantity,
                    price=item.quantity * item.menuitem.price,
                )
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(user_id=user).delete()
            return order
    
    class Meta:
        meodel = Order
        fields = [
            "user",
        ]

class UpdateOrderSerializer(serializers.ModelSerializer):
    def validate_delivery_crew(self, value):
        if not value.groups.filter(name="DeliveryCrew").exists():
            raise serializers.ValidationError("Invalid delivery crew")
        return value
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get("status", instance.status)
        instance.delivery_crew = validated_data.get("delivery_crew", instance.delivery_crew)
        instance.save()
        return instance
    
    class Meta:
        model = Order
        fields = ["status", "delivery_crew"]
