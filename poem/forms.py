from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from poem.models import Author
from poem.models import DayPoem
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
        ]

class DayPoemForm(forms.ModelForm):
    class Meta:
        model = DayPoem
        fields = [
            'poem',
            'day',
        ]

    def clean_day(self):

        poem_id = self.cleaned_data['poem'].id
        day = self.cleaned_data['day']
        today = timezone.now().date()

        # If `day` is None, it means we are about to remove the poem as a
        # daily poem. These errors are not applicable to that scenario.
        if day is not None:
            # Make sure that the requested day doesn't already have a poem.
            if DayPoem.objects.filter(day=day).count() > 0:
                raise forms.ValidationError(_('A poem has already been designated to the given date.'))

            # Make sure that the given poem hasn't already been queued.
            if DayPoem.objects.filter(poem_id=poem_id, day__gte=today).count() > 0:
                raise forms.ValidationError(_('This poem is already queued as a daily poem.'))

        return day
