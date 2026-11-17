from django.db import models


class BloodInventory(models.Model):

    BLOOD_GROUPS = [
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
    ]

    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUPS,
        unique=True
    )

    units_available = models.PositiveIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_group} - {self.units_available} units"
class PatientRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FULFILLED', 'Fulfilled'),
    ]

    patient = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )

    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BloodInventory.BLOOD_GROUPS)
    units_required = models.PositiveIntegerField(default=1)
    hospital_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15)
    required_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group} - {self.status}"