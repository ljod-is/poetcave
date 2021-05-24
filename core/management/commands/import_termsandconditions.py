from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from os import path
from termsandconditions.models import TermsAndConditions

# Remember, this import script is a one-time thing, so we're not going by
# best-practices for re-usability or configurability. It is only here so that
# we can develop the first terms and conditions in markdown and import them
# easily during development.

SLUG_NAME = 'notkunarskilmalar'
NAME = 'Notkunarskilmálar'

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            filename = path.join(settings.BASE_DIR, '..', 'data', 'termsandconditions.md')
            with open(filename, 'r') as f:
                text = f.read()
        except:
            print('Error: Failed opening input file for reading. See code.')
            quit(1)

        if TermsAndConditions.objects.count() > 0:
            print('Error: Terms and conditions already exist.')
            print('       If you still want to import, please remove all instances of')
            print('       TermsAndConditions from the database and try again.')
            print('       Exiting for safety.')
            quit()

        TermsAndConditions(
            slug=SLUG_NAME,
            name=NAME,
            version_number=Decimal('1.00'),
            text=text,
            date_active=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).save()
