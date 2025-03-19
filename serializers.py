from rest_framework import serializers
from .models import Category, Product, Size, Color, AttributeValue, AttributeOption, ProductAttribute, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'parent_name', 'is_active']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'display_name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'display_name', 'hex_code']

class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ['id', 'value', 'display_value']

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    option_value = serializers.CharField(source='option.display_value', read_only=True)
    option_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AttributeValue
        fields = [
            'id', 'attribute', 'attribute_name',
            'option', 'option_value', 'option_display'
        ]
    
    def get_option_display(self, obj):
        if obj.option:
            return {
                'id': obj.option.id,
                'value': obj.option.value,
                'display_value': obj.option.display_value
            }
        return None

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    attributes = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug',
            'category', 'category_name', 'category_slug',
            'price', 'stock', 'is_active',
            'description', 'images', 'attributes',
            'created_at'
        ]

    def get_attributes(self, obj):
        attributes = {}
        for value in obj.attribute_values.all():
            if value.option:
                attr_name = value.attribute.name
                attributes[attr_name] = {
                    'id': value.option.id,
                    'value': value.option.value,
                    'display_value': value.option.display_value
                }
        return attributes