import yaml
from django.core.management.base import BaseCommand
from core.models import Shop, Category, Product, ProductPrice

class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', type=str, help='Путь к YAML файлу для импорта')

    def handle(self, *args, **kwargs):
        yaml_file = kwargs['yaml_file']
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        
        shop_data = data.get('shop')
        if not shop_data:
            self.stdout.write(self.style.ERROR("Нет данных магазина"))
            return

        
        if isinstance(shop_data, dict):
            shop_name = shop_data.get('name')
            shop_file_url = shop_data.get('file_url', '')
        else:
            shop_name = shop_data
            shop_file_url = ''

        shop, created = Shop.objects.get_or_create(
            name=shop_name,
            defaults={'file_url': shop_file_url}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Магазин {shop.name} создан"))
        else:
            self.stdout.write(f"Магазин {shop.name} уже существует")

        
        category_mapping = {}
        categories_data = data.get('categories', [])
        for cat_data in categories_data:
            external_id = cat_data.get('id')
            name = cat_data.get('name')
            category, cat_created = Category.objects.get_or_create(name=name)
            category.shops.add(shop)
            category_mapping[external_id] = category
            if cat_created:
                self.stdout.write(self.style.SUCCESS(f"Категория {name} создана"))
            else:
                self.stdout.write(f"Категория {name} уже существует")

        
        goods_data = data.get('goods', [])
        for good in goods_data:
            cat_id = good.get('category')
            category = category_mapping.get(cat_id)
            if not category:
                self.stdout.write(self.style.WARNING(f"Категория с id {cat_id} не найдена. Пропуск товара {good.get('name')}"))
                continue

            product, prod_created = Product.objects.get_or_create(
                name=good.get('name'),
                category=category,
                defaults={'description': good.get('model', '')}
            )
            price = good.get('price')
            quantity = good.get('quantity', 0)
            ProductPrice.objects.update_or_create(
                product=product, shop=shop,
                defaults={'price': price, 'quantity': quantity}
            )
            self.stdout.write(self.style.SUCCESS(f"Товар {product.name} импортирован/обновлён"))

        self.stdout.write(self.style.SUCCESS("Импорт завершён"))
