from django.db import models
from django.utils import timezone
from inventory.models import Medicine, Supplier, Batch
from auditlog.registry import auditlog

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [('draft','Draft'),('sent','Sent to Supplier'),('partial','Partially Received'),('received','Fully Received'),('cancelled','Cancelled')]
    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_auto_generated = models.BooleanField(default=False)

    def __str__(self): return f"PO #{self.po_number}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            last = PurchaseOrder.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.po_number = f"PO-{timezone.now().strftime('%Y%m')}-{num:04d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity_ordered
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.medicine.name} x {self.quantity_ordered}"

class GoodsReceiptNote(models.Model):
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    received_date = models.DateField(default=timezone.now)
    invoice_number = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"GRN #{self.grn_number}"

    def save(self, *args, **kwargs):
        if not self.grn_number:
            last = GoodsReceiptNote.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.grn_number = f"GRN-{timezone.now().strftime('%Y%m')}-{num:04d}"
        super().save(*args, **kwargs)

class GRNItem(models.Model):
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity_received = models.PositiveIntegerField()
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    manufacture_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12)

    def __str__(self): return f"{self.medicine.name} - {self.batch_number}"

class SupplierLedger(models.Model):
    TRANSACTION_CHOICES = [('purchase','Purchase'),('payment','Payment'),('return','Return'),('adjustment','Adjustment')]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='ledger')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    transaction_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.supplier.name} - {self.transaction_type} - {self.amount}"

auditlog.register(PurchaseOrder)
auditlog.register(GoodsReceiptNote)
