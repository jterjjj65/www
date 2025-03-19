from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from .models import (
    ProductType, 
    Category, 
    Product, 
    AttributeGroup,
    ProductAttribute,
    AttributeOption,
    AttributeValue,
    Color,
    ProductImage
)

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    mptt_level_indent = 20  # отступ для уровней вложенности

    def display_name(self, obj):
        return format_html(
            '<div style="margin-left:{}px">{}</div>',
            obj.level * self.mptt_level_indent,
            obj.name
        )

class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    extra = 1

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'attribute_group', 'required', 'order']
    list_filter = ['attribute_group', 'type', 'required']
    list_editable = ['order', 'required']
    search_fields = ['name']
    inlines = [AttributeOptionInline]
    prepopulated_fields = {'code': ('name',)}

@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'order']
    list_filter = ['product_type']
    list_editable = ['order']
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "option" and request.method == "POST":
            attribute_id = request.POST.get('attribute')
            if attribute_id:
                kwargs["queryset"] = AttributeOption.objects.filter(attribute_id=attribute_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            # Исправленный фильтр для атрибутов
            formset.form.base_fields['attribute'].queryset = \
                ProductAttribute.objects.filter(
                    attribute_group__product_type=obj.category.product_type
                )
        return formset

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
        'stock',  # Добавляем stock в list_display
        'category',
        'is_active'
    ]
    list_filter = ['category', 'is_active']
    list_editable = ['price', 'stock', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AttributeValueInline, ProductImageInline]

    def get_form(self, request, obj=None, **kwargs):
        # Сохраняем объект для использования в inline формах
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    fieldsets = (
        ('Основное', {
            'fields': (
                'name', 
                'slug',
                'category',
                'description',
            )
        }),
        ('Цены и наличие', {
            'fields': (
                'price',
                'stock',
                'is_active'
            )
        }),
        ('Системное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = (
            'admin/js/jquery.init.js',
            'admin/js/attribute_filter.js',
        )

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'colored_hex_code', 'order']
    list_editable = ['order']
    search_fields = ['name', 'display_name']

    def colored_hex_code(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 0 10px;">{}</span>',
            obj.hex_code,
            obj.hex_code
        )
    colored_hex_code.short_description = 'HEX код'
