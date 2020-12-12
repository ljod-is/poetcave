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
]
