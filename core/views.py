from core.forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

def main(request):
    return render(request, 'core/main.html')


@login_required
def profile(request):

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('profile'))

    else:
        form = ProfileForm(instance=request.user)

    ctx = {
        'form': form,
    }
    return render(request, 'core/profile.html', ctx)
