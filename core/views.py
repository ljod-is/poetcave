import frontmatter
import json
import os
import zipfile
from article.models import Article
from core.forms import ProfileForm
from core.forms import RegistrationForm
from datetime import datetime
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django_registration.backends.activation.views import (
    RegistrationView as BaseRegistrationView,
)
from core.models import User
from markdown2 import markdown
from poem.forms import AuthorForm
from poem.models import Author
from poem.models import Poem
from tempfile import TemporaryDirectory


def main(request):
    # Check for daily poem.
    poem = Poem.objects.filter(daypoems__day=timezone.now().date()).first()

    articles = Article.objects.visible_to(request.user).filter(
        editorial_status="published"
    )[0 : settings.NEWEST_ARTICLE_COUNT]

    # Set news article to display if no daily poem.
    frontpage_article = None
    if poem is None:
        frontpage_article = Article.objects.filter(
            editorial_status="published",
            editorial_timing__gte=timezone.now().replace(hour=0, minute=0, second=0),
            editorial_timing__lte=timezone.now().replace(hour=23, minute=59, second=59),
        ).first()

    # Authors with private paths.
    private_path_authors = Author.objects.exclude(private_path=None)

    ctx = {
        # Will be None if no daily poem.
        "poem": poem,
        "articles": articles,
        "frontpage_article": frontpage_article,
        "private_path_authors": private_path_authors,
    }
    return render(request, "core/main.html", ctx)


def team(request):
    # These are looked up separately because they are probably displayed
    # differently in the interface and so just returning one `users` list and
    # determining which is which in the interface would just convolute the
    # template code instead of this bit.
    superusers = User.objects.filter(is_superuser=True)
    moderators = User.objects.filter(is_moderator=True)

    ctx = {
        "superusers": superusers,
        "moderators": moderators,
    }
    return render(request, "core/user/team/list.html", ctx)


def user(request, username):
    try:
        # Only users with privileges are viewable here.
        user = User.objects.filter(Q(is_superuser=True) | Q(is_moderator=True)).get(
            username=username
        )
    except User.DoesNotExist:
        raise Http404

    ctx = {
        "user": user,
    }
    return render(request, "core/user/team/user.html", ctx)


def about(request, page=None):
    PAGE_DIR = "core/templates/core/about"

    # Default to "index.md".
    if page is None:
        page = "index"

    # We don't trust your kind of input around here.
    known_pages = os.listdir(PAGE_DIR)
    if "%s.md" % page not in known_pages:
        raise Http404

    with open("%s/%s.md" % (PAGE_DIR, page)) as f:
        # Read file.
        body = f.read()
        fm = frontmatter.loads(body)

        # Get frontmatter data.
        sign = fm.get("title")

        # Get markdown data.
        content = markdown(fm.content)

    ctx = {
        "sign": sign,
        "content": content,
    }
    return render(request, "core/about.html", ctx)


@login_required
def profile(request):
    author = request.user.author

    password_form = PasswordChangeForm(request.user)
    author_form = AuthorForm(instance=author)
    form = ProfileForm(instance=request.user)

    if request.method == "POST":
        author_form = AuthorForm(request.POST, instance=author)
        form = ProfileForm(request.POST, instance=request.user)

        if author_form.is_valid() and form.is_valid():
            # Check for password change.
            # If password change fails, we don't want to redirect back to the
            # profile with success, but rather for the password form to
            # express the errors to users and allow them to try again.
            password_ok = False
            if (
                request.POST.get("old_password")
                or request.POST.get("new_password1")
                or request.POST.get("new_password2")
            ):
                password_form = PasswordChangeForm(request.user, request.POST)
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, password_form.user)

                    messages.add_message(
                        request, messages.SUCCESS, _("Password updated.")
                    )

                    # Okay because changing passwords succeeded.
                    password_ok = True
            else:
                # Okay because changing passwords wasn't even attempted.
                password_ok = True

            # Even if password change didn't succeed, we still believe in the
            # main form data at this point, so we might as well save it.
            if author_form.has_changed() or form.has_changed():
                author_form.save()
                form.save()
                messages.add_message(request, messages.SUCCESS, _("Profile updated."))

            # Let's not redirect if we want the password form to express
            # errors to the user.
            if password_ok:
                return redirect(reverse("profile"))

    ctx = {
        "password_form": password_form,
        "author_form": author_form,
        "form": form,
    }
    return render(request, "core/user/profile.html", ctx)


# Our custom registration form, that accounts for the Author object needing
# to be created at the same time.
class RegistrationView(BaseRegistrationView):
    def dispatch(self, request, *args, **kwargs):
        author_form = AuthorForm()
        form = RegistrationForm()

        if request.method == "POST":
            author_form = AuthorForm(request.POST)
            form = RegistrationForm(request.POST)

            if author_form.is_valid() and form.is_valid():
                with transaction.atomic():
                    # Trigger the underlying registration mechanism, which
                    # deals with sending the confirmation email and such.
                    new_user = self.register(form)

                    # Save the author data.
                    author = author_form.save()

                    # And tie the user and author data together. This is an
                    # extra hit to the database, but apparently we can't
                    # change the form data above before saving it.
                    author.user_id = new_user.id
                    author.save()

                    return redirect(self.get_success_url())

        ctx = {
            "author_form": author_form,
            "form": form,
        }
        return render(request, "core/user/registration/register.html", ctx)


@login_required
def user_delete(request):
    return render(request, "core/user/delete.html")


@login_required
def user_delete_confirm(request):
    request.user.author.delete()
    request.user.delete()
    return redirect(reverse("logout"))


@login_required
def retrieve_data_download(request):
    # Plan:
    # 1. Create temporary directory.
    # 2. Place data in temporary directory.
    # 3. Create zip from temporary directory.
    # 4. Delete temporary directory.
    # 5. Read zip file into memory.
    # 6. Delete zip file.
    # 7. Push zip data to browser.

    # A function that imitates "zip -r <zipfile> <directory>".
    # Provided in an answer from George V. Reilly, here:
    # https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    def make_zipfile(output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    # Compiles user data into text that can be written directly to a file.
    def compile_user_data():
        # Short-hand.
        u = request.user

        lines = [
            "%s: %s" % (_("Username"), u.username),
            "%s: %s" % (_("Email"), u.email),
            "%s: %s" % (_("Name"), u.contact_name),
            "%s: %s" % (_("Address"), u.contact_address),
            "%s: %s" % (_("Postal code"), u.contact_postal_code),
            "%s: %s" % (_("Place"), u.contact_place),
            "%s: %s" % (_("Phone"), u.contact_phone),
            "%s: %s" % (_("Last updated"), u.date_updated),
            "%s: %s" % (_("Author name"), u.author.name),
            "%s: %s" % (_("Author name (accusative)"), u.author.name_dative),
            "%s: %s" % (_("Author birth-year"), u.author.year_born),
            "%s: %s" % (_("Author death-year"), u.author.year_dead or ""),
            "%s: %s" % (_("About"), u.author.about),
        ]

        return "\r\n".join(lines)

    # Name of the output zip file and corresponding folder.
    package_name = "%s.%s.%s" % (
        settings.INSTANCE_NAME,
        request.user.username,
        timezone.now().strftime("%Y-%m-%d.%H-%M-%S"),
    )

    # See: https://docs.python.org/3/library/tempfile.html#tempfile-examples
    with TemporaryDirectory() as temp_dirname:
        # Create bundle directory.
        package_dir = os.path.join(temp_dirname, package_name)
        os.mkdir(package_dir)

        # Write user data to file.
        user_data = compile_user_data()
        with open(os.path.join(package_dir, "%s.txt" % _("User data")), "w") as f:
            f.write(user_data)

        # Create poem directory (inside bundle directory).
        poems_dir = os.path.join(package_dir, _("Poems"))
        os.mkdir(poems_dir)

        # Write poems to bundle.
        poems = Poem.objects.filter(author__user_id=request.user.id)
        for poem in poems:
            # Write poem text into its own text file.
            with open(os.path.join(poems_dir, "%s.txt" % poem.name), "w") as f:
                f.write(poem.body)

        # Write poems' metadata.
        poems_meta_fields = [
            "about",
            "editorial.status",
            "editorial.user",
            "editorial.timing",
            "editorial.reason",
            "date_created",
            "date_updated",
        ]
        poems_meta = {}
        for poem in poems:
            poem_meta = {}
            for fieldname in poems_meta_fields:
                if "." in fieldname:
                    # We support **one** level down for sub-fields, because
                    # it's not worth abstracting any more than that.
                    # Feel free to improve.
                    loc = fieldname.find(".")
                    fieldvalue = getattr(
                        getattr(poem, fieldname[:loc]), fieldname[loc + 1 :]
                    )
                else:
                    fieldvalue = getattr(poem, fieldname)
                if type(fieldvalue) is datetime:
                    fieldvalue = fieldvalue.strftime("%Y-%m-%d.%H-%M-%S")
                if type(fieldvalue) is str:
                    fieldvalue = fieldvalue
                if type(fieldvalue) is User:
                    fieldvalue = fieldvalue.username
                poem_meta[fieldname] = fieldvalue
            poems_meta[poem.name] = poem_meta
        with open(os.path.join(package_dir, "%s.json" % _("Poem metadata")), "w") as f:
            f.write(
                json.dumps(poems_meta, ensure_ascii=False, sort_keys=True, indent=2)
            )

        # Zip it!
        zip_filename = "%s.zip" % package_dir
        make_zipfile(zip_filename, package_dir)

        # Get the content for delivery, before it vanishes, which it will do
        # when we leave the "with TemporaryDirectory()" section.
        with open(zip_filename, "rb") as f:
            package_data = f.read()

    # Push the content to the user as a zip file for download.
    response = HttpResponse(package_data, content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s.zip" % package_name
    return response


@login_required
def reject_terms(request):
    ctx = {
        "rejecting_terms": True,
    }
    return render(request, "core/user/delete.html", ctx)
