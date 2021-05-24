from core.models import User
from django import forms
from django.utils.translation import ugettext as _
from django_registration.forms import RegistrationForm as BaseRegistrationForm

# A custom email form field which checks if the email address is already
# taken. This is done instead of simply having the email-field as unique,
# because we are working with data that already has duplicates and we want to
# use moving forward. So we want to retain email duplicates from the past, but
# reject them in new registrations.
class UniqueEmailField(forms.EmailField):
    def validate(self, value):
        super().validate(value)
        if User.objects.filter(email=value).count() > 0:
            raise forms.ValidationError(_('Email address is already in use.'))

class RegistrationForm(BaseRegistrationForm):
    email = UniqueEmailField()

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

    def clean_email(self):
        # Make email unchangeable. If we make it changeable in the future,
        # there should be a mechanism for verifying the new address.
        return self.instance.email;

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
