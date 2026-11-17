from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import BloodInventory, PatientRequest
from django.db import models

def inventory_view(request):
    blood_groups = BloodInventory.objects.all().order_by('blood_group')

    return render(
        request,
        'bloodbank/inventory.html',
        {'blood_groups': blood_groups}
    )


@login_required
def patient_request_view(request):
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "Please complete your user profile first.")
        return redirect('dashboard')

    if request.user.userprofile.role != 'PATIENT':
        messages.error(request, "Only patient accounts can request blood.")
        return redirect('dashboard')

    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '').strip()
        blood_group = request.POST.get('blood_group', '')
        units_required = request.POST.get('units_required', '')
        hospital_name = request.POST.get('hospital_name', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        required_date_text = request.POST.get('required_date', '')

        valid_groups = [group[0] for group in BloodInventory.BLOOD_GROUPS]

        try:
            units_required = int(units_required)
            required_date = date.fromisoformat(required_date_text)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid number of units and date.")
            return render(
                request,
                'bloodbank/patient_request.html',
                {'blood_groups': BloodInventory.BLOOD_GROUPS}
            )

        if (
            not patient_name
            or not hospital_name
            or not contact_number
            or blood_group not in valid_groups
            or units_required < 1
            or required_date < date.today()
        ):
            messages.error(request, "Please enter valid details in every field.")
            return render(
                request,
                'bloodbank/patient_request.html',
                {'blood_groups': BloodInventory.BLOOD_GROUPS}
            )

        PatientRequest.objects.create(
            patient=request.user,
            patient_name=patient_name,
            blood_group=blood_group,
            units_required=units_required,
            hospital_name=hospital_name,
            contact_number=contact_number,
            required_date=required_date,
        )

        messages.success(
            request,
            "Your blood request has been submitted successfully!"
        )
        return redirect('dashboard')

    return render(
        request,
        'bloodbank/patient_request.html',
        {'blood_groups': BloodInventory.BLOOD_GROUPS}
    )
@login_required
def my_blood_requests_view(request):
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "Please complete your user profile first.")
        return redirect('dashboard')

    if request.user.userprofile.role != 'PATIENT':
        messages.error(request, "Only patient accounts can view patient blood requests.")
        return redirect('dashboard')

    blood_requests = PatientRequest.objects.filter(
        patient=request.user
    ).order_by('-created_at')

    return render(
        request,
        'bloodbank/my_blood_requests.html',
        {'blood_requests': blood_requests}
    )
def hospital_blood_requests_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "Please complete your user profile first.")
        return redirect('dashboard')

    if request.user.userprofile.role != 'HOSPITAL':
        messages.error(request, "Only hospital staff can view all patient blood requests.")
        return redirect('dashboard')

    
    blood_requests = PatientRequest.objects.all().order_by('-created_at')

    # Search by patient name or hospital name
    search_query = request.GET.get('search', '').strip()

    if search_query:
        blood_requests = blood_requests.filter(
            models.Q(patient_name__icontains=search_query) |
            models.Q(hospital_name__icontains=search_query)
        )

    # Filter by blood group
    selected_blood_group = request.GET.get('blood_group', '')

    if selected_blood_group:
        blood_requests = blood_requests.filter(
            blood_group=selected_blood_group
        )

    # Filter by request status
    selected_status = request.GET.get('status', '')

    if selected_status:
        blood_requests = blood_requests.filter(
            status=selected_status
        )


    pending_count = PatientRequest.objects.filter(status='PENDING').count()
    approved_count = PatientRequest.objects.filter(status='APPROVED').count()
    fulfilled_count = PatientRequest.objects.filter(status='FULFILLED').count()
    rejected_count = PatientRequest.objects.filter(status='REJECTED').count()

   
    return render(
        request,
        'bloodbank/hospital_blood_requests.html',
        {
            'blood_requests': blood_requests,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'fulfilled_count': fulfilled_count,
            'rejected_count': rejected_count,

            # Search and filter values
            'search_query': search_query,
            'selected_blood_group': selected_blood_group,
            'selected_status': selected_status,
        }
    )
