from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import RegistrationView
from django_registration.backends.activation.views import ActivationView
from core import views
from core.forms import RegistrationForm

urlpatterns = [
    path('', views.main, name='main'),

    # Registration entry page.
    path(
        'register/',
        RegistrationView.as_view(
            form_class=RegistrationForm,
            template_name='user/registration/register.html',
            email_body_template = 'user/mail/activation_body.txt',
            email_subject_template = 'user/mail/activation_subject.txt',
            success_url=reverse_lazy('registration_complete')
        ),
        name='register'
    ),

    # Registration complete, not yet activated.
    path(
        'register/complete/',
        TemplateView.as_view(
            template_name='user/registration/registration_complete.html'
        ),
        name='registration_complete',
    ),

    # Landing page for activating from email link.
    path(
        'register/activate/<str:activation_key>/',
        ActivationView.as_view(
            success_url=reverse_lazy('activation_complete')
        ),
        name='activate',
    ),

    # Activation complete.
    path(
        'register/activation-complete/',
        TemplateView.as_view(
            template_name='user/registration/activation_complete.html'
        ),
        name="activation_complete",
    ),

    # Login.
    path(
        'user/login/',
        auth_views.LoginView.as_view(
            template_name='user/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    # Logout.
    path('user/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # User profile.
    path('user/profile/', views.profile, name='profile'),

    # Change password. (Still disabled and profile update used instead.)
    #path(
    #    'user/change-password/',
    #    auth_views.PasswordChangeView.as_view(
    #        template_name='user/password_change.html',
    #        success_url = reverse_lazy('profile')
    #    ),
    #    name='password_change'
    #),
]
