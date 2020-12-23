from core.models import User
from django import forms
from django_registration.forms import RegistrationForm as BaseRegistrationForm

class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'contact_name',
            'contact_address',
            'contact_postal_code',
            'contact_place',
            'contact_phone',
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'contact_name',
            'contact_address',
            'contact_postal_code',
            'contact_place',
            'contact_phone',
        ]
