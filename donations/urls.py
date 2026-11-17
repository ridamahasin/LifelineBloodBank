from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.donation_form_view, name='donation_request'),
]