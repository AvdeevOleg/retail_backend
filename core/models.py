from django.contrib.auth.models import User
from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=255)
    file_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    shops = models.ManyToManyField(Shop, related_name="categories")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return self.name


class ProductPrice(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="prices"
    )
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="product_prices"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)  # наличие товара

    class Meta:
        unique_together = ("product", "shop")

    def __str__(self):
        return f"{self.product.name} в {self.shop.name} – {self.price}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("cart", "Корзина"),
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("completed", "Завершён"),
        ("cancelled", "Отменён"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Заказ {self.id} – {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} от {self.shop.name} x {self.quantity}"


class UserContact(models.Model):
    CONTACT_TYPES = [
        ("phone", "Телефон"),
        ("address", "Адрес"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contacts")
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} – {self.contact_type}: {self.value}"
