from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Patient
from .forms import PatientForm

@login_required
def dashboard(request):
    search = request.GET.get("search")
    if search:
        patients = Patient.objects.filter(last_name__icontains=search).order_by("last_name")
    else:
        patients = Patient.objects.all()

    return render(request, "patients/dashboard.html", {"patients": patients, "search": search})

@login_required
def patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    measurements = patient.measurements.order_by("-timestamp")
    context = {"patient": patient,"measurements": measurements}
    return render(request, "patients/patient.html", context)

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

@login_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient info modified successfully.")
            return redirect("patients:patient", patient_id=patient_id)
    else:
        form = PatientForm(instance=patient)

    return render(request, "patients/edit_patient.html", {"patient": patient, "form": form})

@login_required
@require_POST
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.delete()
    messages.success(request, "Patient deleted successfully from database.")
    return redirect("patients:dashboard")
