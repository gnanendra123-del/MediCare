from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

class UserCreateForm(forms.ModelForm):
    ROLE_CHOICES = [('', 'Select Role'), ('Admin','Admin'), ('Pharmacist','Pharmacist'), ('StoreManager','Store Manager'), ('Accountant','Accountant')]
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, widget=forms.Select(attrs={'class':'form-select'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['username','first_name','last_name','email']}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_staff'].widget = forms.CheckboxInput(attrs={'class':'form-check-input'})
