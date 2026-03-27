from django.db import models
from django.utils import timezone
from datetime import timedelta
from auditlog.registry import auditlog

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Categories'

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    drug_license = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

    class Meta:
        ordering = ['-created_at']

class Medicine(models.Model):
    UNIT_CHOICES = [('strip','Strip'),('box','Box'),('piece','Piece'),('bottle','Bottle'),('vial','Vial'),('tube','Tube'),('sachet','Sachet')]
    SCHEDULE_CHOICES = [('OTC','OTC'),('H','Schedule H'),('H1','Schedule H1'),('X','Schedule X'),('G','Schedule G')]
    FORM_CHOICES = [('tablet','Tablet'),('capsule','Capsule'),('syrup','Syrup'),('injection','Injection'),('drops','Drops'),('ointment','Ointment'),('cream','Cream'),('powder','Powder'),('inhaler','Inhaler'),('other','Other')]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medicines')
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='tablet')
    strength = models.CharField(max_length=50, blank=True, help_text='e.g. 500mg, 10ml')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='strip')
    hsn_code = models.CharField(max_length=20, blank=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    schedule = models.CharField(max_length=5, choices=SCHEDULE_CHOICES, default='OTC')
    prescription_required = models.BooleanField(default=False)
    default_supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=10)
    rack_location = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.name} ({self.brand})"

    class Meta:
        ordering = ['-created_at']

    @property
    def total_stock(self):
        return sum(b.quantity for b in self.batches.filter(quantity__gt=0, is_active=True))

    @property
    def is_low_stock(self):
        return self.total_stock <= self.reorder_level

class Batch(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    manufacture_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.medicine.name} - Batch {self.batch_number}"

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def days_to_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

    @property
    def expiry_status(self):
        days = self.days_to_expiry
        if days < 0: return 'expired'
        elif days <= 30: return 'critical'
        elif days <= 60: return 'warning'
        elif days <= 90: return 'caution'
        return 'ok'

    class Meta:
        ordering = ['expiry_date']

auditlog.register(Medicine)
auditlog.register(Batch)
auditlog.register(Supplier)
