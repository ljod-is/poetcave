from core.forms import ProfileForm
from core.forms import RegistrationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django_registration.backends.activation.views import RegistrationView as BaseRegistrationView
from poem.forms import AuthorForm

def main(request):
    return render(request, 'core/main.html')


@login_required
def profile(request):

    author = request.user.author

    password_form = PasswordChangeForm(request.user)
    author_form = AuthorForm(instance=author)
    form = ProfileForm(instance=request.user)

    if request.method == 'POST':
        author_form = AuthorForm(request.POST, instance=author)
        form = ProfileForm(request.POST, instance=request.user)

        if author_form.is_valid() and form.is_valid():

            # Check for password change.
            # If password change fails, we don't want to redirect back to the
            # profile with success, but rather for the password form to
            # express the errors to users and allow them to try again.
            password_ok = False
            if request.POST.get('old_password') or request.POST.get('new_password1') or request.POST.get('new_password2'):
                password_form = PasswordChangeForm(request.user, request.POST)
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, password_form.user)

                    messages.add_message(request, messages.SUCCESS, _('Password updated.'))

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
                messages.add_message(request, messages.SUCCESS, _('Profile updated.'))

            # Let's not redirect if we want the password form to express
            # errors to the user.
            if password_ok:
                return redirect(reverse('profile'))

    ctx = {
        'password_form': password_form,
        'author_form': author_form,
        'form': form,
    }
    return render(request, 'user/profile.html', ctx)


# Our custom registration form, that accounts for the Author object needing
# to be created at the same time.
class RegistrationView(BaseRegistrationView):
    def dispatch(self, request, *args, **kwargs):

        author_form = AuthorForm()
        form = RegistrationForm()

        if request.method == 'POST':
            author_form = AuthorForm(request.POST)
            form = RegistrationForm(request.POST)

            if author_form.is_valid() and form.is_valid():
                with transaction.atomic():
                    # Trigger the underlying registration mechanism, which
                    # deals with sending the confirmation email and such.
                    new_user = thing = self.register(form)

                    # Save the author data.
                    author = author_form.save()

                    # And tie the user and author data together. The reason
                    # we don't do this before the user creation is because we
                    # want to inherit the underlying user creation process by
                    # using the self.register method above.
                    new_user.author_id = author.id
                    new_user.save()

                    return redirect(self.get_success_url())

        ctx = {
            'author_form': author_form,
            'form': form,
        }
        return render(request, 'user/registration/register.html', ctx)