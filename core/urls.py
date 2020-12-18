from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django_registration.backends.activation.views import RegistrationView
from core import views
from core.forms import RegistrationForm

urlpatterns = [
    path('', views.main),
    path('accounts/register/', RegistrationView.as_view(form_class=RegistrationForm)),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # We're not using this for now, since passwords are changed through the
    # profile, but this code remains in case we'll want to change the flow.
    #path(
    #    'accounts/password_change/',
    #    auth_views.PasswordChangeView.as_view(
    #        template_name='registration/change_password_form.html',
    #        success_url = '/'
    #    ),
    #    name='change_password'
    #),
]
