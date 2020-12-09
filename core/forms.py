from core.models import User
from django_registration.forms import RegistrationForm as BaseRegistrationForm

class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'name',
            'name_dative',
            'birth_year',
            'about',
            'contact_name',
            'contact_address',
            'contact_postal_code',
            'contact_place',
            'contact_phone',
        ]
