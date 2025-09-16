from django.contrib import admin
from .models import Sale, SaleItem, Cart, PaymentRecord, Refund


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['line_total']


class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'cashier', 'total_amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'cashier']
    search_fields = ['sale_number', 'cashier__username']
    readonly_fields = ['sale_number', 'change_amount', 'created_at', 'updated_at']
    inlines = [SaleItemInline, PaymentRecordInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('sale_number', 'cashier', 'status', 'notes')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'amount_paid', 'change_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'discount', 'line_total']
    list_filter = ['sale__created_at']
    search_fields = ['sale__sale_number', 'product__name']
    readonly_fields = ['line_total']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'line_total', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'product__name']


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['sale', 'payment_method', 'amount', 'reference_number', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['sale__sale_number', 'reference_number']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['sale', 'sale_item', 'quantity_refunded', 'refund_amount', 'reason', 'processed_by', 'created_at']
    list_filter = ['reason', 'created_at', 'processed_by']
    search_fields = ['sale__sale_number', 'sale_item__product__name']
    date_hierarchy = 'created_at'
