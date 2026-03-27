from django import forms
from .models import Prescription

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['customer', 'doctor_name', 'doctor_phone', 'hospital', 'prescription_date', 'image', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class':'form-select'}),
            'doctor_name': forms.TextInput(attrs={'class':'form-control'}),
            'doctor_phone': forms.TextInput(attrs={'class':'form-control'}),
            'hospital': forms.TextInput(attrs={'class':'form-control'}),
            'prescription_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }
