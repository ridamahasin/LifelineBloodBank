from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from .models import UserProfile
from bloodbank.models import BloodInventory

def home_view(request):
    return render(request, "useraccounts/home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        role = request.POST.get("role", "")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        elif len(password) < 8:
            messages.error(request, "Password must contain at least 8 characters.")

        elif role not in ["DONOR", "PATIENT", "HOSPITAL"]:
            messages.error(request, "Please select a valid account type.")

        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username is already taken.")

        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email is already registered.")

        else:
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )

                    UserProfile.objects.create(
                        user=user,
                        role=role,
                        phone=phone,
                        address=address
                    )

                messages.success(
                    request,
                    "Account created successfully! You can now log in."
                )
                return redirect("login")

            except Exception:
                messages.error(
                    request,
                    "Unable to create your account. Please try again."
                )

    return render(request, "useraccounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "useraccounts/login.html")
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    profile = UserProfile.objects.get(user=request.user)

    from donations.models import Donation

    # Get all eight blood groups, including groups with zero units.
    blood_groups = []

    for group_code, group_name in BloodInventory.BLOOD_GROUPS:
        inventory = BloodInventory.objects.filter(
            blood_group=group_code
        ).first()

        # Get available units.
        units = inventory.units_available if inventory else 0

        # Determine stock status.
        if units == 0:
            stock_status = "OUT"
        elif units < 5:
            stock_status = "LOW"
        else:
            stock_status = "AVAILABLE"

        # Store blood group, units, and status.
        blood_groups.append({
            "blood_group": group_code,
            "units_available": units,
            "stock_status": stock_status,
        })

    # Show donation history only to donors.
    if profile.role == "DONOR":
        donations = Donation.objects.filter(
            donor=request.user
        ).order_by("-created_at")
    else:
        donations = Donation.objects.none()

    return render(
        request,
        "useraccounts/dashboard.html",
        {
            "profile": profile,
            "donations": donations,
            "blood_groups": blood_groups,
        }
    )
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect("login")

