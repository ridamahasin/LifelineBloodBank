from django.contrib import admin
from django.urls import path, include
from useraccounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('', include('useraccounts.urls')),
    path('bloodbank/', include('bloodbank.urls')),
    path("donations/", include("donations.urls")),
]