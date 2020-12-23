from django import forms
from poem.models import Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            'name',
            'name_dative',
            'birth_year',
            'about',
        ]
