from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .forms import PatientForm

@login_required
def dashboard(request):
    patients = Patient.objects.all()
    return render(request, "patients/dashboard.html", {"patients": patients})

@login_required
def new_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.assigned_doctor = request.user
            obj.save()

            messages.success(request, "Patient added successfully.")
            return redirect("patients:dashboard")
    else:
        form = PatientForm()

    return render(request, "patients/new_patient.html", {"form": form})
