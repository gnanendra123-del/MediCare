from django.contrib import admin
from .models import Medicine, Batch, Category, Supplier

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'schedule', 'total_stock', 'is_active']
    list_filter = ['category', 'schedule', 'form', 'is_active']
    search_fields = ['name', 'brand', 'generic_name', 'barcode']

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch_number', 'expiry_date', 'quantity', 'selling_price']
    list_filter = ['is_active']
    search_fields = ['medicine__name', 'batch_number']

admin.site.register(Category)
admin.site.register(Supplier)
