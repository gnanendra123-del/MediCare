from django.db import models
from customers.models import Customer
from auditlog.registry import auditlog

class Prescription(models.Model):
    STATUS_CHOICES = [('pending','Pending Verification'),('verified','Verified'),('dispensed','Dispensed'),('rejected','Rejected')]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='prescriptions')
    doctor_name = models.CharField(max_length=200)
    doctor_phone = models.CharField(max_length=20, blank=True)
    hospital = models.CharField(max_length=200, blank=True)
    prescription_date = models.DateField()
    image = models.ImageField(upload_to='prescriptions/')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Rx #{self.id} - {self.customer.name} ({self.prescription_date})"

auditlog.register(Prescription)
