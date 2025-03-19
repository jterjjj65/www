from django.db.models import Q
from .models import Product, AttributeValue

class CatalogService:
    @staticmethod
    def get_filtered_products(queryset, filters=None):
        """Фильтрация товаров с оптимизацией запросов"""
        if not filters:
            return queryset

        # Фильтры по цене
        if filters.get('min_price'):
            queryset = queryset.filter(price__gte=filters['min_price'])
        if filters.get('max_price'):
            queryset = queryset.filter(price__lte=filters['max_price'])

        # Фильтр по категории
        if filters.get('category'):
            queryset = queryset.filter(
                Q(category__slug=filters['category']) |
                Q(category__parent__slug=filters['category'])
            )

        # Фильтр по атрибутам
        if filters.get('attributes'):
            for attr_code, value in filters['attributes'].items():
                queryset = queryset.filter(
                    attribute_values__attribute__code=attr_code,
                    attribute_values__option__value=value
                )

        # Фильтр по наличию
        if filters.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)

        return queryset.distinct()