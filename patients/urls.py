from django.urls import path

from . import views

app_name = "patients"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("patient/new/", views.new_patient, name="new_patient"),
    path("patient/<int:patient_id>/", views.patient, name="patient"),
    path("patient/<int:patient_id>/edit/", views.edit_patient, name="edit_patient"),
    path("patient/<int:patient_id>/delete/", views.delete_patient, name="delete_patient"),
]
