from core.forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _

def main(request):
    return render(request, 'core/main.html')


@login_required
def profile(request):

    password_form = PasswordChangeForm(request.user)
    form = ProfileForm(instance=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():

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
            if form.has_changed():
                form.save()
                messages.add_message(request, messages.SUCCESS, _('Profile updated.'))

            # Let's not redirect if we want the password form to express
            # errors to the user.
            if password_ok:
                return redirect(reverse('profile'))

    ctx = {
        'password_form': password_form,
        'form': form,
    }
    return render(request, 'user/profile.html', ctx)
