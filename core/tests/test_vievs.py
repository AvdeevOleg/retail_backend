from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import Product


class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testclient1", password="testclientpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Создадим тестовый товар
        self.product = Product.objects.create(
            name="Test Product", description="Test", category_id=1
        )

    def test_get_product_list(self):
        url = reverse("product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_detail(self):
        url = reverse("product-detail", args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cart_addition(self):
        url = reverse("cart")
        data = {
            "product_id": self.product.id,
            "shop_id": 1,
            "price": 1000,
            "quantity": 2,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
