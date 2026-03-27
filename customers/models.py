from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog

class Customer(models.Model):
    GENDER_CHOICES = [('M','Male'),('F','Female'),('O','Other')]
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    total_purchases = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.name} ({self.phone})"

    class Meta:
        ordering = ['-created_at']

    @property
    def loyalty_tier(self):
        if self.total_purchases >= 10000: return 'Gold'
        elif self.total_purchases >= 5000: return 'Silver'
        return 'Regular'

class MedicineReminder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reminders')
    medicine_name = models.CharField(max_length=200)
    reminder_date = models.DateField()
    notes = models.TextField(blank=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Reminder: {self.customer.name} - {self.medicine_name}"

auditlog.register(Customer)
