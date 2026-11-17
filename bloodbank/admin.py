from django.contrib import admin, messages
from django.db import transaction
from .models import BloodInventory, PatientRequest


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'units_available', 'last_updated')
    list_filter = ('blood_group',)
    search_fields = ('blood_group',)
    ordering = ('blood_group',)


@admin.register(PatientRequest)
class PatientRequestAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'blood_group',
        'units_required',
        'hospital_name',
        'required_date',
        'status',
        'created_at',
    )

    list_filter = ('blood_group', 'status', 'required_date')

    search_fields = (
        'patient_name',
        'hospital_name',
        'contact_number',
        'patient__username',
    )

    ordering = ('-created_at',)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        previous = None

        if change:
            previous = PatientRequest.objects.select_for_update().get(
                pk=obj.pk
            )

        # Deduct blood only when the request first becomes fulfilled.
        if obj.status == 'FULFILLED':
            if previous is None:
                messages.error(
                    request,
                    "Save the request first before marking it fulfilled."
                )
                obj.status = 'PENDING'

            elif previous.status != 'FULFILLED':
                inventory = BloodInventory.objects.select_for_update().filter(
                    blood_group=obj.blood_group
                ).first()

                if inventory is None:
                    messages.error(
                        request,
                        f"No inventory record exists for {obj.blood_group}."
                    )
                    obj.status = previous.status

                elif inventory.units_available < obj.units_required:
                    messages.error(
                        request,
                        f"Insufficient {obj.blood_group} blood inventory. "
                        f"Available: {inventory.units_available} units; "
                        f"required: {obj.units_required} units."
                    )
                    obj.status = previous.status

                else:
                    inventory.units_available -= obj.units_required
                    inventory.save()

        super().save_model(request, obj, form, change)
