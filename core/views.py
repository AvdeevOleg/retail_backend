# Create your views here.
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, permissions, serializers, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import IntegerField, Serializer
from rest_framework.views import APIView

from .models import Order, OrderItem, Product
from .serializers import (AddOrderItemSerializer, OrderSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetSerializer, ProductSerializer,
                          RegistrationSerializer, UserContactSerializer,
                          UserSerializer)


class ProductCountSerializer(Serializer):
    count = IntegerField()


@extend_schema(responses=OpenApiResponse(ProductCountSerializer))
@api_view(["GET"])
@cache_page(60 * 2)
def cached_product_list(request):

    products = Product.objects.all()

    return Response({"count": products.count()})


class TriggerErrorView(APIView):
    """
    APIView для тестового исключения.
    Используется для проверки интеграции Sentry/Rollbar.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        raise Exception("Test exception for Sentry")


# Регистрация
class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]


# Авторизация


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])
        user = UserSerializer(token.user).data
        return Response({"token": token.key, "user": user})


# Товары


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# Характеристики товара


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# Корзина


class CartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, user):
        cart, created = Order.objects.get_or_create(user=user, status="cart")
        return cart

    def get(self, request):
        cart = self.get_cart(request.user)
        serializer = OrderSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart = self.get_cart(request.user)
        serializer = AddOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            OrderItem.objects.create(
                order=cart,
                product_id=serializer.validated_data["product_id"],
                shop_id=serializer.validated_data["shop_id"],
                price=serializer.validated_data["price"],
                quantity=serializer.validated_data["quantity"],
            )
            return Response(
                {"detail": "Товар добавлен в корзину"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        cart = self.get_cart(request.user)
        item_id = request.data.get("item_id")
        try:
            item = cart.items.get(id=item_id)
            item.delete()
            return Response(
                {"detail": "Товар удалён из корзины"},
                status=status.HTTP_200_OK
            )
        except OrderItem.DoesNotExist:
            return Response(
                {"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND
            )


# Подтверждение заказа


class OrderConfirmationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Order.objects.filter(user=request.user, status="cart").first()
        if not cart or not cart.items.exists():
            return Response(
                {"detail": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Адрес доставки, если указан
        delivery_address = request.data.get("delivery_address")
        if delivery_address:
            cart.delivery_address = delivery_address
        cart.status = "new"
        cart.save()
        # Уведомление по email покупателю и администратору
        subject = f"Заказ №{cart.id} подтверждён"
        message = "Ваш заказ принят и находится в обработке."
        recipient_list = [request.user.email]
        admin_email = settings.ADMIN_EMAIL
        try:
            send_mail(subject, message,
                      settings.DEFAULT_FROM_EMAIL, recipient_list)
            send_mail(
                f"Новый заказ №{cart.id}",
                f"Новый заказ от {request.user.username}",
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
            )
        except Exception:
            pass
        serializer = OrderSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Список заказов


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).exclude(status="cart")


# Детали заказа


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Управление контактами пользователя


class UserContactCreateView(generics.CreateAPIView):
    serializer_class = UserContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        contact_type = serializer.validated_data.get("contact_type")
        if contact_type == "phone":
            if self.request.user.contacts.filter(
                contact_type="phone"
            ).exists():
                raise serializers.ValidationError("Телефон уже добавлен.")
        elif contact_type == "address":
            address_contacts = self.request.user.contacts.filter(
                contact_type='address'
            )
            if address_contacts.count() >= 5:
                raise serializers.ValidationError(
                    "Можно добавить не более 5 адресов.")
        serializer.save(user=self.request.user)


class UserContactDeleteView(generics.DestroyAPIView):
    serializer_class = UserContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.contacts.all()


# Сброса пароля


class PasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Формируем ссылку, используя SERVER_DOMAIN из настроек
            reset_link = (
                f"http://{settings.SERVER_DOMAIN}/api/password-reset-confirm/"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                subject="Сброс пароля",
                message=f"Ссылка для сброса пароля: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return Response(
                {"detail": "Ссылка для сброса пароля отправлена на ваш email"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Подтверждение сброса пароля


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Пароль успешно сброшен."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
