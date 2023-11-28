from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User, Group

from .models import MenuItem

class MenuItemTestCase(APITestCase):
    def set(self):
        self.customer_user = User.objects.create_user(username="customer", password="test1234!")
        self.delivery_user = User.objects.create_user(username="delivery", password="test1234!")
        self.manager_user = User.objects.create_user(username="manager", password="test1234!")

        self.manager_group = Group.objects.create(name="Manager")
        self.delivery_group = Group.objects.create(name="DeliveryCrew")
        self.customer_group = Group.objects.create(name="Customer")

        self.customer_user.groups.add(self.customer_group)
        self.delivery_user.groups.add(self.delivery_group)
        self.manager_user.groups.add(self.manager_group)

        self.client = APIClient()

        MenuItem.objects.create(name="Item 1", price=10)
        MenuItem.objects.create(name="Item 2", price=200)

    def manager_only_can_change_menu(self):
        self.client.force_authenticate(user=self.manager_user)

        item_id = 1
        update_data = {"name": "Item chnaged", "price": 20}
        response = self.client.post(f"/menu-items/{item_id}/", update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        update_item = MenuItem.objects.get(id=item_id)
        self.assertEqual(update_item.name, update_data["name"])
        self.assertEqual(update_item.price, update_data["price"])


