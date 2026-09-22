import time
import random
from decimal import Decimal
from prettytable import PrettyTable
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from ...models import Patient, Measurement
from ...anomaly import evaluate_measurement

TICK_INTERVAL = 2

SAMPLE_PATIENTS = [
    {
        "first_name": "Sofia",
        "last_name": "Karagianni",
        "age": 42,
        "gender": "F",
        "room": "202",
        "bed": "1",
        "baseline_heart_rate": 88,
        "baseline_spo2": 96,
        "baseline_temperature": Decimal("36.7"),
        "baseline_respiratory_rate": 16,
        "baseline_systolic_bp": 132,
        "baseline_diastolic_bp": 85,
    },
    {
        "first_name": "Kostas",
        "last_name": "Antonopoulos",
        "age": 34,
        "gender": "M",
        "room": "203",
        "bed": "2",
        "baseline_heart_rate": 65,
        "baseline_spo2": 99,
        "baseline_temperature": Decimal("36.4"),
        "baseline_respiratory_rate": 13,
        "baseline_systolic_bp": 115,
        "baseline_diastolic_bp": 72,
    },
    {
        "first_name": "Giorgos",
        "last_name": "Oikonomou",
        "age": 83,
        "gender": "M",
        "room": "204",
        "bed": "3",
        "baseline_heart_rate": 82,
        "baseline_spo2": 93,
        "baseline_temperature": Decimal("37.0"),
        "baseline_respiratory_rate": 19,
        "baseline_systolic_bp": 148,
        "baseline_diastolic_bp": 92,
    },
    {
        "first_name": "Maria",
        "last_name": "Papadopoulou",
        "age": 67,
        "gender": "F",
        "room": "201",
        "bed": "1",
        "baseline_heart_rate": 72,
        "baseline_spo2": 97,
        "baseline_temperature": Decimal("36.6"),
        "baseline_respiratory_rate": 15,
        "baseline_systolic_bp": 125,
        "baseline_diastolic_bp": 82,
    },
    {
        "first_name": "Nikos",
        "last_name": "Georgiou",
        "age": 45,
        "gender": "M",
        "room": "201",
        "bed": "2",
        "baseline_heart_rate": 68,
        "baseline_spo2": 98,
        "baseline_temperature": Decimal("36.5"),
        "baseline_respiratory_rate": 14,
        "baseline_systolic_bp": 118,
        "baseline_diastolic_bp": 76,
    },
    {
        "first_name": "Elena",
        "last_name": "Dimitriou",
        "age": 78,
        "gender": "F",
        "room": "205",
        "bed": "1",
        "baseline_heart_rate": 80,
        "baseline_spo2": 95,
        "baseline_temperature": Decimal("36.8"),
        "baseline_respiratory_rate": 18,
        "baseline_systolic_bp": 138,
        "baseline_diastolic_bp": 88,
    },
    {
        "first_name": "Dimitris",
        "last_name": "Nikolaou",
        "age": 71,
        "gender": "M",
        "room": "205",
        "bed": "2",
        "baseline_heart_rate": 76,
        "baseline_spo2": 94,
        "baseline_temperature": Decimal("36.9"),
        "baseline_respiratory_rate": 17,
        "baseline_systolic_bp": 142,
        "baseline_diastolic_bp": 90,
    },
    {
        "first_name": "Anna",
        "last_name": "Vasileiou",
        "age": 29,
        "gender": "F",
        "room": "206",
        "bed": "1",
        "baseline_heart_rate": 62,
        "baseline_spo2": 99,
        "baseline_temperature": Decimal("36.3"),
        "baseline_respiratory_rate": 12,
        "baseline_systolic_bp": 110,
        "baseline_diastolic_bp": 70,
    },
]

def generate_measurement(patient, prev):
    """
    Generate measurement based on the patient's baselines and the previous measurement.
    Values drift smoothly using small random steps.
    """
    def drift(previous_value, baseline, max_step, min_value, max_value):
        reversion = (baseline - previous_value) * 0.05
        step = random.uniform(-max_step, max_step) + reversion
        return max(min_value, min(max_value, previous_value + step))

    if prev is None:
        return {
            "heart_rate": int(patient.baseline_heart_rate + random.randint(-3, 3)),
            "spo2": int(patient.baseline_spo2 + random.randint(-1, 1)),
            "temperature": Decimal(str(round(float(patient.baseline_temperature) + random.uniform(-0.2, 0.2), 1))),
            "respiratory_rate": int(patient.baseline_respiratory_rate + random.randint(-2, 2)),
            "systolic_bp": int(patient.baseline_systolic_bp + random.randint(-3, 3)),
            "diastolic_bp": int(patient.baseline_diastolic_bp + random.randint(-2, 2)),
        }

    return {
        "heart_rate": int(round(drift(prev.heart_rate, patient.baseline_heart_rate, 3, 30, 220))),
        "spo2": int(round(drift(prev.spo2, patient.baseline_spo2, 1, 50, 100))),
        "temperature": Decimal(str(round(drift(float(prev.temperature), float(patient.baseline_temperature), 0.2, 34.0, 42.0), 1))),
        "respiratory_rate": int(round(drift(prev.respiratory_rate, patient.baseline_respiratory_rate, 2, 5, 40))),
        "systolic_bp": int(round(drift(prev.systolic_bp, patient.baseline_systolic_bp, 3, 60, 250))),
        "diastolic_bp": int(round(drift(prev.diastolic_bp, patient.baseline_diastolic_bp, 2, 30, 150))),
    }


class Command(BaseCommand):
    help = "Continuously generate simulated sign measurements for all patients."

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=TICK_INTERVAL,
            help=f"Seconds between measurement rounds (default: {TICK_INTERVAL})",
        )

    def handle(self, *args, **options):
        interval = options["interval"]
        if not Patient.objects.exists():
            Patient.objects.bulk_create([Patient(**data) for data in SAMPLE_PATIENTS])

        patients = list(Patient.objects.all())

        self.stdout.write(f"Simulating {len(patients)} patients every {interval}s. Ctrl+C to stop.")

        # track last measurement per patient for smooth drift
        last = {patient.id: patient.measurements.first() for patient in patients}

        channel_layer = get_channel_layer()

        try:
            tick = 0
            while True:
                tick += 1
                table = PrettyTable()
                table.field_names = ["Patient", "Room", "HR", "SpO2", "Temp", "RR", "BP", "Status"]

                measurements = []
                evaluations = {}
                for patient in patients:
                    data = generate_measurement(patient, last.get(patient.id))
                    measurements.append(Measurement(patient=patient, **data))

                    status, anomalies = evaluate_measurement(data)
                    evaluations[patient.id] = {
                        # overall status
                        "status": status,
                        # vitals that are abnormal only
                        "vital_statuses": {anomaly["vital_sign"]: anomaly["severity"] for anomaly in anomalies},
                    }

                    if patient.status != status:
                        patient.status = status
                        patient.save(update_fields=["status"])
                        
                        # broadcast status change to dashboard
                        async_to_sync(channel_layer.group_send)(
                            "dashboard",
                            {
                                "type": "status_update",
                                "data": {
                                    "patient_id": patient.id,
                                    "status": status,
                                }
                            }
                        )

                    table.add_row([
                        f"{patient.first_name} {patient.last_name}",
                        patient.room,
                        data["heart_rate"],
                        f"{data['spo2']}%",
                        f"{data['temperature']}°C",
                        data["respiratory_rate"],
                        f"{data['systolic_bp']}/{data['diastolic_bp']}",
                        status.upper(),
                    ])

                self.stdout.write(f"\n{'=' * 28} Tick {tick} {'=' * 28}")
                self.stdout.write(table.get_string())

                time.sleep(interval)

                for measurement in Measurement.objects.bulk_create(measurements):
                    last[measurement.patient_id] = measurement
                    ev = evaluations[measurement.patient_id]

                    async_to_sync(channel_layer.group_send)(
                        f"patient_{measurement.patient_id}",
                        {
                            "type": "new_measurement",
                            "data": {
                                "timestamp": measurement.timestamp.strftime("%d %b %Y, %H:%M:%S"),
                                "heart_rate": measurement.heart_rate,
                                "spo2": measurement.spo2,
                                "temperature": str(measurement.temperature),
                                "respiratory_rate": measurement.respiratory_rate,
                                "systolic_bp": measurement.systolic_bp,
                                "diastolic_bp": measurement.diastolic_bp,
                                "status": ev["status"],
                                "vital_statuses": ev["vital_statuses"],
                            },
                        },
                    )
        except KeyboardInterrupt:
            self.stdout.write("\nSimulator stopped.")
