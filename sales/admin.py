from django.contrib import admin
from .models import Sale, SaleItem
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'sale_date', 'total_amount', 'payment_method', 'status']
    inlines = [SaleItemInline]
