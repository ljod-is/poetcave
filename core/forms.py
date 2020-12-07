from core.models import User
from django_registration.forms import RegistrationForm as BaseRegistrationForm

class RegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        model = User
