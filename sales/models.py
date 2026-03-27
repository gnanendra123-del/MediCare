from django.db import models
from django.utils import timezone
from customers.models import Customer
from inventory.models import Medicine, Batch
from prescriptions.models import Prescription
from auditlog.registry import auditlog

class Sale(models.Model):
    PAYMENT_CHOICES = [('cash','Cash'),('upi','UPI'),('card','Card'),('credit','Credit')]
    STATUS_CHOICES = [('draft','Draft'),('completed','Completed'),('cancelled','Cancelled'),('refunded','Refunded')]

    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, default='paid')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    loyalty_points_used = models.PositiveIntegerField(default=0)
    loyalty_points_earned = models.PositiveIntegerField(default=0)

    def __str__(self): return f"Invoice #{self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Sale.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{num:04d}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=6)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=6)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        qty = Decimal(str(self.quantity))
        unit_price = Decimal(str(self.unit_price))
        discount_pct = Decimal(str(self.discount_percent))
        gst_rate = Decimal(str(self.gst_rate))
        gross = unit_price * qty
        discount = gross * (discount_pct / Decimal('100'))
        self.taxable_amount = gross - discount
        self.gst_amount = self.taxable_amount * (gst_rate / Decimal('100'))
        self.total_price = self.taxable_amount + self.gst_amount
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.medicine.name} x {self.quantity}"

auditlog.register(Sale)
