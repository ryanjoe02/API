from rest_framework import serializers


from .models import MenuItem, Category, Cart


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
