from django.contrib import admin
from .models import Patient, Measurement

admin.site.register(Patient)
admin.site.register(Measurement)
