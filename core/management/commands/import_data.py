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

from poem.models import Author


# A utility function for returning rows as a dictionary.
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# A utility function for returning a timezone-aware datetime if it's a
# datetime object, but a None if it's None.
def awarize(dt):
    if dt is None:
        return None
    else:
        # This may provoke an exception which should be handled by the calling
        # function as usual.
        return timezone.make_aware(dt)


class Command(BaseCommand):

    connection = None


    def handle(self, *args, **kwargs):

        try:
            self.connection = connections['old']

            self.remove_duplicates()

            self.import_users()

            self.import_authors()

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

        existing_user_ids = ','.join([str(i) for i in User.objects.all().values_list('id', flat=True)]) or '0'

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
                WHERE
                    `id` NOT IN (%s)
            ''' % existing_user_ids)

            for row in dictfetchall(cursor):

                # Create new user.
                user = User()

                # We'll keep the ID, basically because we can. This also means
                # that we don't have to check if the row already exists.
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
                User.objects.filter(
                    id=user.id
                ).update(
                    date_updated=awarize(row['last_updated'])
                )

                print(' done')


    def import_authors(self):

        existing_author_ids = ','.join([str(i) for i in Author.objects.all().values_list('id', flat=True)]) or '0'

        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    `p`.`id`,
                    `p`.`name`,
                    `p`.`name_thagufall`,
                    `p`.`born`,
                    `p`.`dead`,
                    `p`.`info`,
                    `p`.`last_updated`,
                    `u`.`id` AS `user_id`
                FROM
                    `cube_poets` AS `p`
                    INNER JOIN `users` AS `u` ON `u`.`poet` = `p`.`id`
                WHERE
                    `p`.`id` NOT IN (%s)
            ''' % existing_author_ids)

            for row in dictfetchall(cursor):
                author = Author()

                # We'll keep the ID, basically because we can. This also means
                # that we don't have to check if the row already exists.
                author.id = row['id']

                # Figure out what to do with crazy year data.
                try:
                    year_born = int(row['born'])

                    # When users give a two-digit year, we'll assume they mean
                    # 1900-and-that.
                    if len(str(year_born)) == 2:
                        year_born += 1900

                except ValueError:
                    # This mean we ran into some weird value, and we're forced
                    # to say it's None. There are lots of strange values in
                    # the original database.
                    year_born = None

                author.name = row['name']
                author.name_dative = row['name_thagufall']
                author.year_born = year_born
                author.year_dead = row['dead'] or None
                author.about = row['info']

                # This is possible because we imported the users with their
                # original ID.
                author.user_id = row['user_id']

                print('Saving author "%s"...' % author.name, end='', flush=True)
                author.save()

                # Copy data about last update. This results in an extra call
                # to the database, but we do this to avoid the triggering of
                # `auto_now` for the field. It doesn't matter, since this
                # script will only be run once and then never again.
                Author.objects.filter(
                    id=author.id
                ).update(
                    date_updated=awarize(row['last_updated'])
                )

                print(' done')
