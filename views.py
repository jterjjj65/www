from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import JsonResponse
from .models import Category, Product, AttributeOption, ProductImage
from .serializers import (
    CategorySerializer, 
    ProductSerializer,
    ProductImageSerializer
)
from .filters import ProductFilter
from django.db import transaction
from django_filters import rest_framework as filters
from .services import CatalogService

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Отключаем пагинацию для категорий
    search_fields = ['name']

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.NumberFilter(field_name="category__id")
    
    class Meta:
        model = Product
        fields = ['category', 'is_active', 'min_price', 'max_price']

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с товарами"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Оптимизация запросов"""
        queryset = super().get_queryset().prefetch_related(
            'images',
            'attribute_values',
            'attribute_values__attribute',
            'attribute_values__option'
        )
        
        filters = {
            'min_price': self.request.query_params.get('min_price'),
            'max_price': self.request.query_params.get('max_price'),
            'category': self.request.query_params.get('category'),
            'in_stock': self.request.query_params.get('in_stock') == 'true',
            'attributes': {
                'size': self.request.query_params.get('size'),
                'color': self.request.query_params.get('color')
            }
        }
        
        return CatalogService.get_filtered_products(queryset, filters)

def get_attribute_options(request, attribute_id):
    """Получение вариантов значений для атрибута"""
    try:
        # Добавляем отладочную информацию
        print(f"Запрос опций для атрибута {attribute_id}")
        
        options = AttributeOption.objects.filter(
            attribute_id=attribute_id
        ).values(
            'id',
            'value',
            'display_value',
            'order'
        ).order_by('order')
        
        data = list(options)
        print(f"Отправляем данные: {data}")
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@transaction.atomic
def create_product(request):
    """Создание товара"""
    if request.method == 'POST':
        try:
            # Логируем данные для отладки
            print("Данные товара:", request.POST)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)