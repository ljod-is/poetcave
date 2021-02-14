from django import forms
from poem.models import Author
from poem.models import Poem

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = [
            'name',
            'name_dative',
            'year_born',
            'about',
        ]

class PoemForm(forms.ModelForm):
    class Meta:
        model = Poem
        fields = [
            'name',
            'body',
            'about',
            'public',
        ]
