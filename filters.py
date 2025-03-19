from django_filters import rest_framework as filters
from .models import Product, Category, AttributeValue

class ProductFilter(filters.FilterSet):
    """Фильтры для товаров каталога"""
    # Фильтры по цене
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Фильтры по категории
    category = filters.CharFilter(field_name='category__slug')
    parent_category = filters.CharFilter(field_name='category__parent__slug')
    
    # Фильтры по наличию
    in_stock = filters.BooleanFilter(method='filter_stock')
    has_images = filters.BooleanFilter(method='filter_images')
    
    # Фильтры по атрибутам
    size = filters.CharFilter(method='filter_size')
    color = filters.CharFilter(method='filter_color')

    class Meta:
        model = Product
        fields = [
            'min_price', 'max_price',
            'category', 'parent_category',
            'in_stock', 'has_images',
            'size', 'color'
        ]

    def filter_stock(self, queryset, name, value):
        """Фильтр по наличию на складе"""
        return queryset.filter(stock__gt=0) if value else queryset

    def filter_images(self, queryset, name, value):
        """Фильтр по наличию изображений"""
        return queryset.filter(images__isnull=False) if value else queryset

    def filter_size(self, queryset, name, value):
        """Фильтр по размеру"""
        return queryset.filter(
            attribute_values__attribute__code='size',
            attribute_values__option__value=value
        ).distinct()

    def filter_color(self, queryset, name, value):
        """Фильтр по цвету"""
        return queryset.filter(
            attribute_values__attribute__code='color',
            attribute_values__option__value=value
        ).distinct()