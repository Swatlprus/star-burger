from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum
from django.db.models import F
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItemQuerySet(models.QuerySet):
    def available(self):
        restaurant_menu = self.filter(availability=True)\
            .select_related('restaurant', 'product')
        return restaurant_menu


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    objects = RestaurantMenuItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def count_price(self):
        total_price = self.annotate(total_price=Sum(F('items__price') * F('items__quantity')))
        return total_price

    def prefetch_items(self):
        prefetch = self.count_price()\
            .exclude(status='Completed')\
            .prefetch_related('items')\
            .prefetch_related('items__product')
        return prefetch


class Order(models.Model):
    STATUS_CHOICES = [
        ('Raw', 'Необработан'),
        ('Assembly', 'Сборка'),
        ('Delivery', 'Доставка'),
        ('Completed', 'Выполнен'),
    ]
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=9,
        choices=STATUS_CHOICES,
        default='Raw',
        db_index=True,
    )
    PAYMENT_CHOICES = [
        ('Cash', 'Наличностью'),
        ('E-money', 'Электронно'),
        ('No choice', 'Не выбрано'),
    ]
    payment = models.CharField(
        verbose_name='Способ оплаты',
        max_length=9,
        choices=PAYMENT_CHOICES,
        default='No choice',
        db_index=True,
    )
    firstname = models.CharField(
        verbose_name='Имя',
        max_length=30,
        blank=False,
        db_index=True,
    )
    lastname = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        blank=False,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        unique=True,
        verbose_name='Телефон',
        db_index=True,
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=255,
        blank=False,
        db_index=True,
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        max_length=500,
        blank=True,
    )
    registrated_at = models.DateTimeField(
        verbose_name='Дата создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='Время звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='Время доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='Ресторан',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id} {self.firstname} {self.lastname}'


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='products',
        verbose_name='Продукты',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )
    order = models.ForeignKey(
        Order,
        related_name="items",
        verbose_name="Заказ",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "элемент заказа"
        verbose_name_plural = "элементы заказа"

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'
