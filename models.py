from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError

class ProductType(models.Model):
    """Тип товара (например: Одежда, Электроника)"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Тип товара'
        verbose_name_plural = 'Типы товаров'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Category(MPTTModel):
    """Категория товаров с поддержкой MPTT"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Тип товара'
    )

    class MPTTMeta:
        order_insertion_by = ['order', 'name']

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField('Значение', max_length=10, unique=True)  # XS, S, M, L и т.д.
    display_name = models.CharField('Отображаемое имя', max_length=50)
    order = models.IntegerField('Порядок', default=0)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'
        ordering = ['order']

    def __str__(self):
        return self.display_name

class Color(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    display_name = models.CharField('Отображаемое имя', max_length=50)
    hex_code = models.CharField('HEX код', max_length=7)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name

class Density(models.Model):
    value = models.IntegerField('Значение', unique=True)  # например, 180, 200 г/м
    description = models.CharField('Описание', max_length=100)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Плотность ткани'
        verbose_name_plural = 'Плотность ткани'
        ordering = ['value']

    def __str__(self):
        return f"{self.value} г/м"

class Product(models.Model):
    """Товар"""
    name = models.CharField('Название', max_length=255)
    slug = models.SlugField(
        'URL',
        unique=True,
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField('Остаток', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    main_image = models.ImageField(
        'Главное изображение',
        upload_to='products/%Y/%m/%d/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='products/%Y/%m/%d/'
    )
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товара'
        ordering = ['order']

class AttributeGroup(models.Model):
    """Группа атрибутов (например, 'Физические характеристики', 'Размеры')"""
    name = models.CharField('Название', max_length=100)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name='attribute_groups',
        verbose_name='Тип товара'
    )
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Группа атрибутов'
        verbose_name_plural = 'Группы атрибутов'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class ProductAttribute(models.Model):
    ATTRIBUTE_TYPES = [
        ('text', 'Текст'),
        ('number', 'Число'),
        ('choice', 'Выбор'),
        ('multiple', 'Множественный выбор'),
        ('color', 'Цвет'),
    ]
    """Атрибут товара (например: Размер, Цвет)"""
    name = models.CharField('Название', max_length=100)
    code = models.SlugField('Код для API', unique=True)
    type = models.CharField('Тип', max_length=10, choices=ATTRIBUTE_TYPES)
    attribute_group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name='Группа атрибутов'
    )
    required = models.BooleanField('Обязательный', default=False)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'
        ordering = ['attribute_group', 'order', 'name']

    def __str__(self):
        return f"{self.attribute_group.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

class AttributeOption(models.Model):
    """Варианты значений для атрибутов типа 'выбор'"""
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Атрибут'
    )
    value = models.CharField('Значение', max_length=100)
    display_value = models.CharField('Отображаемое значение', max_length=100)
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вариант атрибута'
        verbose_name_plural = 'Варианты атрибутов'
        ordering = ['order', 'value']
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name} - {self.display_value}"

class AttributeValue(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='attribute_values',
        null=True,
        blank=True
    )
    attribute = models.ForeignKey(
        'ProductAttribute',
        on_delete=models.CASCADE,
        related_name='values',
        null=True,
        blank=True
    )
    option = models.ForeignKey(
        'AttributeOption',
        on_delete=models.CASCADE,
        related_name='product_values',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибутов'

    def __str__(self):
        return f"{self.product} - {self.attribute}: {self.option if self.option else 'Не указано'}"

    def clean(self):
        # Проверяем соответствие только если option указан
        try:
            if self.option is not None:
                if self.attribute and self.option.attribute_id != self.attribute_id:
                    from django.core.exceptions import ValidationError
                    raise ValidationError({
                        'option': f'Значение не соответствует атрибуту'
                    })
        except AttributeValue.option.RelatedObjectDoesNotExist:
            pass
