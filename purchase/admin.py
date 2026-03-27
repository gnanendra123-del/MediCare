from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, SupplierLedger
admin.site.register(PurchaseOrder)
admin.site.register(SupplierLedger)
