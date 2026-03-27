from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GRNItem

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'expected_delivery', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class':'form-select'}),
            'order_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'expected_delivery': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

class GRNForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptNote
        fields = ['invoice_number', 'invoice_date', 'notes']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class':'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

POItemFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderItem, fields=['medicine','quantity_ordered','unit_price','gst_rate'], extra=3)
GRNItemFormSet = inlineformset_factory(GoodsReceiptNote, GRNItem, fields=['medicine','quantity_received','batch_number','expiry_date','purchase_price','selling_price','mrp'], extra=1)
