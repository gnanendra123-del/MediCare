from django import forms
from .models import Customer, MedicineReminder

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['loyalty_points', 'total_purchases', 'created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'gender': forms.Select(attrs={'class':'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'address': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = MedicineReminder
        exclude = ['customer', 'is_sent', 'created_at']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class':'form-control'}),
            'reminder_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }
