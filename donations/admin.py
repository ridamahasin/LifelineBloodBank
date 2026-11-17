from django.contrib import admin, messages
from django.db import transaction
from .models import Donation
from bloodbank.models import BloodInventory


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'donor',
        'age',
        'blood_group',
        'phone',
        'donation_date',
        'status',
        'created_at',
    )

    list_filter = ('blood_group', 'status', 'donation_date')
    search_fields = ('donor__username', 'phone', 'blood_group')
    ordering = ('-created_at',)
    readonly_fields = ('inventory_updated',)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous = None

        if change:
            previous = Donation.objects.select_for_update().get(pk=obj.pk)

        # Update inventory only when an approved donation is completed.
        if obj.status == 'COMPLETED' and not obj.inventory_updated:
            if previous and previous.status == 'APPROVED':
                inventory, created = BloodInventory.objects.get_or_create(
                    blood_group=obj.blood_group,
                    defaults={'units_available': 0},
                )

                inventory.units_available += 1
                inventory.save()

                obj.inventory_updated = True

            elif previous is None:
                messages.warning(
                    request,
                    "Save the donation as Approved before marking it Completed."
                )
                obj.status = 'PENDING'

            elif previous.status != 'COMPLETED':
                messages.warning(
                    request,
                    "Only an approved donation can be marked Completed."
                )
                obj.status = previous.status
                obj.inventory_updated = previous.inventory_updated

        super().save_model(request, obj, form, change)