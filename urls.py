from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('categories', views.CategoryViewSet, basename='categories')

urlpatterns = [
    # API endpoints через роутер
    path('', include(router.urls)),
    
    # Дополнительные endpoints
    path('attributes/<int:attribute_id>/options/', 
         views.get_attribute_options, 
         name='attribute-options'),
    
    path('products/create/',
         views.create_product,
         name='create-product'),
]