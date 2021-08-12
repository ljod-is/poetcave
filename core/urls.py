from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django_registration.backends.activation.views import ActivationView
from core import views
from core.forms import RegistrationForm
from core.views import RegistrationView
from termsandconditions.views import AcceptTermsView

urlpatterns = [
    path('', views.main, name='main'),

    # Administrators, moderators and such, so that people can contact them and
    # see who is responsible for the web and its contents.
    path('team/', views.team, name='team'),
    path('team/user/<str:username>/', views.user, name='user'),

    # Static pages rendered via markdown templates.
    path('about/<str:page>/', views.about, name='about'),
    path('about/', views.about, name='about'),

    # Registration entry page.
    path(
        'register/',
        RegistrationView.as_view(
            form_class=RegistrationForm,
            template_name='core/user/registration/register.html',
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
            template_name='core/user/registration/registration_complete.html'
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
            template_name='core/user/registration/activation_complete.html'
        ),
        name="activation_complete",
    ),

    # Login.
    path(
        'user/login/',
        auth_views.LoginView.as_view(
            template_name='core/user/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    # Logout.
    path('user/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Reset password.
    path(
        'user/reset-password/',
        auth_views.PasswordResetView.as_view(
            template_name='core/user/password_reset/reset.html',
            email_template_name='core/user/mail/password_reset_body.txt',
            success_url = reverse_lazy('password_reset_requested')
        ),
        name='password_reset'
    ),

    # Password reset requested.
    # NOTE: Django's native mechanism weirdly calls this "done" when there
    # are at least two steps left. We call it "requested".
    path(
        'user/reset-password/requested/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='core/user/password_reset/reset_requested.html'
        ),
        name='password_reset_requested'
    ),

    # Password request confirmed.
    path(
        'user/reset-password/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='core/user/password_reset/reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    # Password request and reset complete.
    path(
        'user/reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='core/user/password_reset/reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # User profile.
    path('user/profile/', views.profile, name='profile'),

    # Change password. (Still disabled and profile update used instead.)
    #path(
    #    'user/change-password/',
    #    auth_views.PasswordChangeView.as_view(
    #        template_name='core/user/password_change.html',
    #        success_url = reverse_lazy('profile')
    #    ),
    #    name='password_change'
    #),

    # Delete user.
    path('user/delete/', views.user_delete, name='user_delete'),
    path('user/delete/confirm/', views.user_delete_confirm, name='user_delete_confirm'),

    # Retrieve personal data.
    path('user/retrieve-data/download/', views.retrieve_data_download, name='retrieve_data_download'),

    # Terms and conditions.
    path(
        'terms/accept/',
        AcceptTermsView.as_view(
            template_name='termsandconditions/terms.html'
        ),
        name='tc_accept_page'
    ),
    path(
        'terms/accept/<slug:slug>/',
        AcceptTermsView.as_view(
            template_name='termsandconditions/terms.html'
        ),
        name='tc_accept_specific_page'
    ),
    path(
        'terms/reject/',
        views.reject_terms,
        name='tc_reject_page'
    ),
]
