from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_view, name='inventory'),
    path('patient-request/', views.patient_request_view, name='patient_request'),
    path('my-blood-requests/', views.my_blood_requests_view, name='my_blood_requests'),
    path('hospital-requests/', views.hospital_blood_requests_view, name='hospital_blood_requests'),
]