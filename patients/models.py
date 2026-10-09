from django.conf import settings
from django.db import models


class Patient(models.Model):
    class Status(models.TextChoices):
        NORMAL = "normal", "Normal"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=1, choices=Gender)
    room = models.CharField(max_length=10)
    bed = models.CharField(max_length=10)
    admission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status, default=Status.NORMAL)
    news2_score = models.PositiveSmallIntegerField(default=0)
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="patients",
    )

    # baseline physiological profile for the simulator
    baseline_heart_rate = models.PositiveSmallIntegerField(default=72)
    baseline_spo2 = models.PositiveSmallIntegerField(default=97)
    baseline_temperature = models.DecimalField(max_digits=4, decimal_places=1, default=36.6)
    baseline_respiratory_rate = models.PositiveSmallIntegerField(default=15)
    baseline_systolic_bp = models.PositiveSmallIntegerField(default=120)
    baseline_diastolic_bp = models.PositiveSmallIntegerField(default=80)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Room {self.room}, Bed {self.bed})"


class Measurement(models.Model):
    heart_rate = models.PositiveSmallIntegerField()  # bpm
    spo2 = models.PositiveSmallIntegerField()  # %
    temperature = models.DecimalField(max_digits=4, decimal_places=1)  # celsius
    respiratory_rate = models.PositiveSmallIntegerField()  # breaths/min
    systolic_bp = models.PositiveSmallIntegerField()  # mmHg
    diastolic_bp = models.PositiveSmallIntegerField()  # mmHg

    timestamp = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="measurements")

    def __str__(self):
        return f"Patient {self.patient_id} @ {self.timestamp:%H:%M:%S}"
