from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Patient

@login_required
def dashboard(request):
    patients = Patient.objects.all()
    return render(request, "patients/dashboard.html", {"patients": patients})
