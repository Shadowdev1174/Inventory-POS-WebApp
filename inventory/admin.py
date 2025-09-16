from django.contrib import admin
from .models import Category, Supplier, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    list_filter = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'selling_price', 'stock_quantity', 'is_low_stock', 'is_active']
    list_filter = ['category', 'supplier', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'supplier', 'sku', 'barcode', 'image', 'is_active')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'minimum_stock')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reason', 'user', 'created_at']
    list_filter = ['movement_type', 'created_at', 'user']
    search_fields = ['product__name', 'reason', 'reference']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
