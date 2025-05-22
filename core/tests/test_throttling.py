from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class ThrottlingTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="client2", password="clientpass456"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_throttling(self):
        url = reverse("product-list")

        for i in range(105):
            response = self.client.get(url)
        self.assertEqual(response.status_code,
                         status.HTTP_429_TOO_MANY_REQUESTS)
