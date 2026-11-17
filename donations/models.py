from django.db import models
from django.contrib.auth.models import User


class Donation(models.Model):

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

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='donations'
    )

    age = models.PositiveIntegerField()
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUPS
    )
    phone = models.CharField(max_length=15)
    donation_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    inventory_updated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} - {self.blood_group}"