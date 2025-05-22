from django.contrib import admin

from .models import (Category, Order, OrderItem, Product, ProductPrice, Shop,
                     UserContact)

admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductPrice)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(UserContact)
