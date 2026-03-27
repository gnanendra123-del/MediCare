from django import forms
from .models import Medicine, Batch, Category, Supplier

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        exclude = ['created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'brand': forms.TextInput(attrs={'class':'form-control'}),
            'generic_name': forms.TextInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-select'}),
            'form': forms.Select(attrs={'class':'form-select'}),
            'strength': forms.TextInput(attrs={'class':'form-control'}),
            'unit': forms.Select(attrs={'class':'form-select'}),
            'hsn_code': forms.TextInput(attrs={'class':'form-control'}),
            'barcode': forms.TextInput(attrs={'class':'form-control'}),
            'schedule': forms.Select(attrs={'class':'form-select'}),
            'default_supplier': forms.Select(attrs={'class':'form-select'}),
            'reorder_level': forms.NumberInput(attrs={'class':'form-control'}),
            'rack_location': forms.TextInput(attrs={'class':'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

class BatchForm(forms.ModelForm):
    # FIX BUG-1: exclude is_active from form so model default=True is always used
    class Meta:
        model = Batch
        exclude = ['medicine', 'created_at', 'is_active']
        widgets = {
            'batch_number': forms.TextInput(attrs={'class':'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'manufacture_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'quantity': forms.NumberInput(attrs={'class':'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'selling_price': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'mrp': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'gst_rate': forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
        }

    def save(self, commit=True):
        batch = super().save(commit=False)
        batch.is_active = True  # always active on create
        if commit:
            batch.save()
        return batch

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['created_at']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['name','contact_person','phone','email','gstin','drug_license']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget = forms.Textarea(attrs={'class':'form-control','rows':3})
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={'class':'form-check-input'})
