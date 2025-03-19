from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """Стандартный пагинатор для каталога"""
    page_size = 12  # Товаров на странице
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Общее количество
            'total_pages': self.page.paginator.num_pages,  # Всего страниц
            'current_page': self.page.number,  # Текущая страница
            'next': self.get_next_link(),  # Ссылка на следующую
            'previous': self.get_previous_link(),  # Ссылка на предыдущую
            'results': data  # Данные текущей страницы
        })

class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })