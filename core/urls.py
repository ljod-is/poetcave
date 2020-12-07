from django.urls import include
from django.urls import path
from core import views

urlpatterns = [
    path('', views.main),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
