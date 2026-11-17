from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Donation


@login_required
def donation_form_view(request):

    # Allow only donor accounts to submit donation requests
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "Please complete your user profile first.")
        return redirect('dashboard')

    if request.user.userprofile.role != 'DONOR':
        messages.error(request, "Only registered donor accounts can submit donation requests.")
        return redirect('dashboard')

    if request.method == 'POST':

        age = request.POST.get('age', '')
        blood_group = request.POST.get('blood_group', '')
        phone = request.POST.get('phone', '').strip()
        donation_date = request.POST.get('donation_date', '')

        # Validate the submitted information
        try:
            age = int(age)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid age.")
            return render(request, 'donations/donation_form.html')

        if age < 18 or age > 100:
            messages.error(request, "Donors must be between 18 and 100 for this form.")
            return render(request, 'donations/donation_form.html')

        valid_groups = [group[0] for group in Donation.BLOOD_GROUPS]

        if blood_group not in valid_groups:
            messages.error(request, "Please select a valid blood group.")
            return render(request, 'donations/donation_form.html')

        if not phone:
            messages.error(request, "Please enter your phone number.")
            return render(request, 'donations/donation_form.html')

        try:
            donation_date = date.fromisoformat(donation_date)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid donation date.")
            return render(request, 'donations/donation_form.html')

        if donation_date < date.today():
            messages.error(request, "Please select today or a future date.")
            return render(request, 'donations/donation_form.html')

        # Save the donation request
        Donation.objects.create(
            donor=request.user,
            age=age,
            blood_group=blood_group,
            phone=phone,
            donation_date=donation_date
        )

        messages.success(
            request,
            "Your donation request was submitted successfully!"
        )

        return redirect('dashboard')

    return render(request, 'donations/donation_form.html')
