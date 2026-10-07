from django.contrib import admin

from .models import Measurement, Patient

admin.site.register(Patient)
admin.site.register(Measurement)
