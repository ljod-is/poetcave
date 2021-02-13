'''
This script is a one-time deal. We'll import the data from the existing
website. Once this import is done and the new website is up and running
feature-complete, this script should be deleted.

There's a bit more hard-coding here than usual for this reason. This will
never become general-purpose.
'''
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from core.models import User


# A utility function for returning rows as a dictionary.
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class Command(BaseCommand):

    connection = None


    def handle(self, *args, **kwargs):

        try:
            self.connection = connections['old']

            self.remove_duplicates()

            self.import_users()

        except KeyboardInterrupt:
            quit(1)


    def remove_duplicates(self):
        # Rather than constantly keeping track of a duplicate in the database,
        # we'll just remove it before dealing with the rest.
        #
        # Normally, we would analyze the database here and figure out
        # duplicates programmatically, but we know there is only one instance,
        # with the user ID 4000, so we'll hard-code this, seeing that this
        # script is a one-off thing.
        with self.connection.cursor() as cursor:
            print('Deleting duplicate data...', end='', flush=True)
            cursor.execute('DELETE FROM `cube_poets` WHERE `id` = 4147')
            cursor.execute('DELETE FROM `users` WHERE `id` = 4000')
            print(' done')


    def import_users(self):

        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    `id`,
                    `user`,
                    `email`,
                    `fullname`,
                    `address`,
                    `postnr`,
                    `place`,
                    `phone`,
                    `shortdescr`,
                    `last_updated`
                FROM
                    `users`
            ''')

            for row in dictfetchall(cursor):

                # Create new user.
                user = User()

                # We'll keep the ID, basically because we can. This also means
                # that we don't have to check if the user already exists.
                user.id = row['id']

                # Technical details.
                user.username = row['user']
                user.email = row['email']

                # Personal details.
                user.contact_name = row['fullname']
                user.contact_address = row['address']
                user.contact_postal_code = row['postnr']
                user.contact_place = row['place']
                user.contact_phone = row['phone']

                print('Saving user "%s"...' % user.username, end='', flush=True)
                user.save()

                # Copy data about last update. This results in an extra call
                # to the database, but we do this to avoid the triggering of
                # `auto_now` for the field. It doesn't matter, since this
                # script will only be run once and then never again.
                date_updated = row['last_updated']
                if date_updated is not None:
                    date_updated = timezone.make_aware(date_updated)
                User.objects.filter(id=user.id).update(date_updated=date_updated)

                print(' done')
