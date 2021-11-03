'''
This script is a one-time deal. We'll import the data from the existing
website. Once this import is done and the new website is up and running
feature-complete, this script should be deleted.

There's a bit more hard-coding here than usual for this reason. This will
never become general-purpose.
'''
from datetime import datetime
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from core.models import User

from poem.models import Author
from poem.models import Bookmark
from poem.models import DayPoem
from poem.models import EditorialDecision
from poem.models import Poem


# These are hard-coded because this script is a one-shot thing, and these are
# the only ones who will have superuser access in the beginning. Superusers
# can manage users. Moderators manage poems, but those are defined in the
# database as `admin`, which we will turn into `is_moderator=True`.
superusers = [
    'david',
    'helgihg',
]


# A utility function for returning rows as a dictionary.
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# A utility function for returning a timezone-aware datetime if it's a
# datetime object, but a None if it's None.
def awarize(dt):
    if dt is None:
        return None
    elif type(dt) is int:
        return timezone.make_aware(datetime.utcfromtimestamp(dt))
    else:
        # This may provoke an exception which should be handled by the calling
        # function as usual.
        if type(dt) is date:
            return timezone.make_aware(datetime(dt.year, dt.month, dt.day))
        else:
            return timezone.make_aware(dt)


# A utility function for figuring out what to do with crazy year data.
def sanitize_year(year):
    try:
        result = int(year)

        # When users give a two-digit year, we'll assume they mean
        # 1900-and-that.
        if len(str(result)) == 2:
            result += 1900

    except ValueError:
        # This mean we ran into some weird value, and we're forced to say it's
        # None. There are lots of strange values in the original database.
        result = None

    return result


class Command(BaseCommand):

    connection = None


    def handle(self, *args, **kwargs):

        try:
            self.connection = connections['old']

            self.remove_duplicates()

            self.import_users()

            self.import_authors()

            self.import_poems()

            self.import_day_poem()

            self.import_bookmarks()

            self.configure_private_paths()

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
        #
        # We also delete certain garbage data, for example day-poems with a
        # poem ID of 0 and those with a nonsensical date.
        with self.connection.cursor() as cursor:
            print('Deleting duplicate data and other garbage...', end='', flush=True)

            # Duplicate user/poet.
            cursor.execute('DELETE FROM `cube_poets` WHERE `id` = 4147')
            cursor.execute('DELETE FROM `users` WHERE `id` = 4000')

            # DayPoem garbage.
            cursor.execute('DELETE FROM `cube_poems_daypoem` WHERE `poem` = 0')
            cursor.execute('DELETE FROM `cube_poems_daypoem` WHERE `day` < "2000-01-01"')

            # Bookmark garbage.
            cursor.execute('DELETE FROM `bookmarks` WHERE `poem_id` = 0 OR `user_id` = 0')

            # Bookmark duplicates.
            cursor.execute('''
                SELECT
                    `id`,
                    `user_id`,
                    `poem_id`
                FROM
                    `bookmarks`
                ORDER BY
                    `user_id`,
                    `poem_id`
            ''')
            last_user_id = None
            last_poem_id = None
            bookmarks_to_delete = [0]
            for row in dictfetchall(cursor):
                if row['user_id'] == last_user_id and row['poem_id'] == last_poem_id:
                    bookmarks_to_delete.append(row['id'])
                last_user_id = row['user_id']
                last_poem_id = row['poem_id']
            cursor.execute(
                'DELETE FROM `bookmarks` WHERE `id` IN (%s)' % ','.join(str(v) for v in bookmarks_to_delete)
            )

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
                    `admin`,
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
                user.is_superuser = user.is_staff = row['user'] in superusers
                user.is_moderator = int(row['admin']) > 0

                # Personal details.
                user.contact_name = row['fullname']
                user.contact_address = row['address']
                user.contact_postal_code = row['postnr']
                user.contact_place = row['place']
                user.contact_phone = row['phone']

                with transaction.atomic():
                    print('Saving user "%s"...' % user.username, end='', flush=True)
                    user.save()

                    # Copy data about last update. This results in an extra
                    # call to the database, but we do this to avoid the
                    # triggering of `auto_now` for the field. It doesn't
                    # matter, since this script will only be run once and then
                    # never again.
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
                    LEFT OUTER JOIN `users` AS `u` ON `u`.`poet` = `p`.`id`
                WHERE
                    `p`.`id` NOT IN (%s)
            ''' % existing_author_ids)

            for row in dictfetchall(cursor):
                author = Author()

                # We'll keep the ID, basically because we can. This also means
                # that we don't have to check if the row already exists.
                author.id = row['id']

                author.name = row['name']
                author.name_dative = row['name_thagufall']
                author.year_born = sanitize_year(row['born'])
                author.year_dead = sanitize_year(row['dead'])
                author.about = row['info']

                # This is possible because we imported the users with their
                # original ID.
                if row['user_id'] is not None:
                    author.user_id = row['user_id']

                with transaction.atomic():
                    print('Saving author "%s"...' % author.name, end='', flush=True)
                    author.save()

                    # Copy data about last update. This results in an extra
                    # call to the database, but we do this to avoid the
                    # triggering of `auto_now` for the field. It doesn't
                    # matter, since this script will only be run once and then
                    # never again.
                    Author.objects.filter(
                        id=author.id
                    ).update(
                        date_updated=awarize(row['last_updated'])
                    )

                    print(' done')


    def import_poems(self):

        # Some poems are by authors that have been deleted, so we'll need to
        # check for their existence.
        author_ids = list(Author.objects.all().values_list('id', flat=True))

        existing_poem_ids = ','.join([str(i) for i in Poem.objects.all().values_list('id', flat=True)]) or '0'

        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    `id`,
                    `name`,
                    `body`,
                    `author`,
                    `sent`,
                    `about`,
                    `accepted`,
                    `visible`,
                    `whyrejected`,
                    `trashed`,
                    `last_updated`
                FROM
                    `cube_poems`
                WHERE
                     `id` NOT IN (%s)
            ''' % existing_poem_ids)

            for row in dictfetchall(cursor):
                poem = Poem()

                poem.id = row['id']
                poem.name = row['name']
                poem.body = row['body']
                poem.about = row['about']

                # Figure out what we can about the editorial status. The new
                # way of storing this information is different from the
                # original website, since we want to minimize the use of
                # different variables to designate the poem's current status
                # in the system.
                editorial = EditorialDecision()
                if row['accepted'] == '-1':
                    editorial.status = 'rejected'
                elif row['accepted'] == '1':
                    editorial.status = 'approved'
                    editorial.timing = awarize(row['sent'])
                else:
                    if row['trashed'] is not None:
                        editorial.status = 'trashed'
                        editorial.timing = awarize(row['trashed'])
                    elif row['visible'] == '1':
                        editorial.status = 'pending'
                        editorial.timing = awarize(row['sent'])
                    else:
                        editorial.status = 'unpublished'
                        editorial.timing = awarize(row['sent'])

                # poem.editorial_timing data sometimes available (see above).
                # poem.editorial_user data not available.
                # poem.editorial_reason data not available.

                # Only attribute poems to authors that actually exist.
                if row['author'] is not None and row['author'] in author_ids:
                    poem.author_id = row['author']

                with transaction.atomic():
                    print('Saving poem "%s"...' % poem.name, end='', flush=True)
                    poem.save()

                    # Set the editorial decision, for the history.
                    editorial.poem = poem
                    editorial.save()

                    # This should always be the most recent editorial
                    # decision, but we only have one now, which will always be
                    # the latest one. We need to save the `poem` again because
                    # the editorial won't exist until the poem exists.
                    poem.editorial = editorial
                    poem.save()

                    # Copy data about last update. This results in an extra
                    # call to the database, but we do this to avoid the
                    # triggering of `auto_now` for the field. It doesn't
                    # matter, since this script will only be run once and then
                    # never again.
                    Poem.objects.filter(
                        id=poem.id
                    ).update(
                        date_updated=awarize(row['last_updated'])
                    )

                    # Do the same for creation, since we have it.
                    Poem.objects.filter(
                        id=poem.id
                    ).update(
                        date_created=awarize(row['sent'])
                    )

                    print(' done')

    def import_day_poem(self):

        existing_daypoems = "'%s'" % "','".join([
            '%s:%s' % (v['poem_id'], v['day'].strftime('%Y-%m-%d')) for v in DayPoem.objects.all().values('poem_id', 'day')
        ])

        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT DISTINCT
                    `d`.`poem`,
                    `d`.`day`
                FROM
                    `cube_poems_daypoem` AS `d`
                    INNER JOIN `cube_poems` AS `p` ON `p`.`id` = `d`.`poem`
                WHERE
                     CONCAT(`d`.`poem`, ':', `d`.`day`) NOT IN (%s)
                ORDER BY
                    `d`.`day`
            ''' % existing_daypoems)

            for row in dictfetchall(cursor):

                daypoem = DayPoem()
                daypoem.poem_id = int(row['poem'])
                daypoem.day = awarize(row['day'])

                print('Saving daypoem for %s...' % row['day'], end='', flush=True)
                daypoem.save()
                print(' done')

    def import_bookmarks(self):

        existing_bookmarks = "'%s'" % "','".join([
            '%s:%s' % (b['user_id'], b['poem_id']) for b in Bookmark.objects.all().values('poem_id', 'user_id')
        ])

        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT
                    `b`.`user_id`,
                    `b`.`poem_id`
                FROM
                    `bookmarks` AS `b`
                INNER JOIN
                    `users` AS `u` ON (
                        `u`.`id` = `b`.`user_id`
                    )
                INNER JOIN
                    `cube_poems` AS `p` ON (
                        `p`.`id` = `b`.`poem_id`
                    )
                WHERE
                    CONCAT(`b`.`user_id`, ':', `b`.`poem_id`) NOT IN (%s)
            ''' % existing_bookmarks)

            for row in dictfetchall(cursor):
                bookmark = Bookmark()
                bookmark.user_id = row['user_id']
                bookmark.poem_id = row['poem_id']

                print(
                    'Saving bookmark (user_id %d, poem_id %d)...' % (row['user_id'], row['poem_id']),
                    end='',
                    flush=True
                )
                bookmark.save()
                print(' done')

    def configure_private_paths(self):

        # These were produced by shell scripting around in the original's
        # website. It didn't make sense to create some fancy code to parse
        # it, seeing that this is a one-time thing.
        #
        # What we "path" here is effectively a username, at least in most
        # cases. The new website doesn't have that as a rule, but it seems to
        # be more or less the tradition in the old website.
        paths_to_author_ids = {
            'miriam': 2851,
            'steindor': 3119,
            'baj': 68,
            #'gudny': 3427, # Not on original website.
            'hugskot': 925,
            'hjorvarpetursson': 641,
            #'stefan': 9, # Does not exist.
            'selma': 1361,
            'kristjanf': 2361,
            'gunni': 117,
            'johannaidunn': 2501,
            'sigrunh': 115,
            'thursi': 1339,
            'skar': 670,
            'ingibjorg': 1471,
            'arnar': 1380,
            'hildur': 536,
            'sirry': 1408,
            'stefanbheidarsson': 194,
            'svarri': 1527,
            'hjalti': 94,
            'harhar': 1110,
            'hm': 558,
            'stefanf': 1553,
            'sofus': 1961,
            'david': 13,
            'heida': 257,
            'janus': 378,
            'Toshiki': 364,
            'solvifannar': 1687,
        }

        for private_path in paths_to_author_ids:
            author_id = paths_to_author_ids[private_path]
            try:
                author = Author.objects.get(id=author_id)
            except:
                import ipdb; ipdb.set_trace()
            if author.private_path is None:
                print('Setting private path for author "%s"...' % author, end='', flush=True)
                author.private_path = private_path
                author.save()
                print(' done')
