from django.db import models


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    # for string converstion
    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
    # category cannot be deleted before all the related menu items are deleted
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
