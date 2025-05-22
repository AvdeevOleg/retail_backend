import os

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.core.management import call_command


# ✅ Задача 1: Отправка письма с подтверждением заказа
@shared_task(serializer='json')
def send_order_confirmation_email(to_email, order_id):
    subject = f"Подтверждение заказа №{order_id}"
    message = f"Спасибо за ваш заказ! Номер заказа: {order_id}"
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, [to_email])
    print(f"Письмо отправлено на {to_email}")
    return f"Email отправлен на {to_email}"


# ✅ Задача 2: Импорт данных из YAML-файла
@shared_task
def import_products_task(yaml_path=None):
    if not yaml_path or not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Файл {yaml_path} не найден.")
    call_command('import_products', yaml_path)
    return f"Импорт товаров из {yaml_path} завершён."
