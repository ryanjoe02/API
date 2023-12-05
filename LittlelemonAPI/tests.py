from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User, Group

from .models import MenuItem, Category


class MenuItemTestCase(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username="customer", password="test1234!"
        )
        self.delivery_user = User.objects.create_user(
            username="delivery", password="test1234!"
        )
        self.manager_user = User.objects.create_user(
            username="manager", password="test1234!"
        )

        self.manager_group = Group.objects.create(name="Manager")
        self.delivery_group = Group.objects.create(name="DeliveryCrew")
        self.customer_group = Group.objects.create(name="Customer")

        self.manager_group.user_set.add(self.manager_user)
        self.delivery_group.user_set.add(self.delivery_user)
        self.customer_group.user_set.add(self.customer_user)

        self.client = APIClient()
        
        category = Category.objects.create(title="Category 1", slug="category 1")
        self.item1 = MenuItem.objects.create(title="Item 1", price=10, featured=True, category=category)
        self.item2 = MenuItem.objects.create(title="Item 2", price=200, featured=False, category=category)

    def test_manager_only_can_change_menu(self):
        self.client.force_login(self.manager_user)

        item_id = self.item1.id
        update_data = {"title": "Item chnaged", "price": 20}
        response = self.client.patch(reverse("menu-item", args=[item_id]), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        update_item = MenuItem.objects.get(id=item_id)
        self.assertEqual(update_item.title, update_data["title"])
        self.assertEqual(update_item.price, update_data["price"])

    def test_crew_cannot_change_menu(self):
        self.client.force_login(self.delivery_user)

        item_id = self.item2.id
        update_data = {"title": "Item chnaged", "price": 20}
        response = self.client.patch(reverse("menu-items", args=[item_id]), update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

