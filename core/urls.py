from django.urls import path
from .views import (
    RegistrationView, CustomAuthToken, ProductListView, ProductDetailView,
    CartView, OrderConfirmationView, OrderListView, OrderDetailView,
    UserContactCreateView, UserContactDeleteView,
    PasswordResetView, PasswordResetConfirmView, TriggerErrorView, cached_product_list
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('order/confirm/', OrderConfirmationView.as_view(), name='order-confirm'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('contacts/', UserContactCreateView.as_view(), name='contact-add'),
    path('contacts/<int:pk>/', UserContactDeleteView.as_view(), name='contact-delete'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('cached-products/', cached_product_list, name='cached-products'),
]

