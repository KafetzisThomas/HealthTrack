
THRESHOLDS = {
    # MEDICAL SOURCES
    # ---------------

    # National Early Warning Score 2 (NEWS2):
    # - https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf
    # - https://www.mdcalc.com/calc/10083/national-early-warning-score-news-2

    # American Heart Association (AHA):
    # - https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings

    # bpm: normal = 60 - 100, <50 = bradycardia, >130 = severe tachycardia
    "heart_rate": {"critical": (40, 130), "warning": (50, 100)},

    # %: normal = 95 - 100
    "spo2": {"critical": (91,), "warning": (94,)},

    # celsius: normal = ~ 36.5 - 37.5, >=38.1 = fever, <=35.0 = clinical hypothermia
    "temperature": {"critical": (35.0, 39.1), "warning": (36.0, 38.1)},

    # breaths/min: normal = 12 - 20, highly sensitive indicator of deterioration
    "respiratory_rate": {"critical": (8, 25), "warning": (11, 21)},

    # mmHg: normal = 90 - 120, >=180 = hypertensive crisis, <=90 = clinical hypotension
    "systolic_bp": {"critical": (90, 180), "warning": (100, 140)},

    # mmHg: normal = 60 - 80, >=120 = hypertensive crisis, <=60 = hypotension
    "diastolic_bp": {"critical": (50, 120), "warning": (60, 90)},
}


DISPLAY_NAMES = {
    "heart_rate": "Heart Rate",
    "spo2": "SpO₂",
    "temperature": "Temperature",
    "respiratory_rate": "Respiratory Rate",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
}


def calculate_news2(measurement_data):
    """
    Calculate the exact NEWS2 integer score (0-20+).
    """
    score = 0

    respiratory_rate = float(measurement_data.get("respiratory_rate", 0))
    if respiratory_rate <= 8:
        score += 3
    elif 9 <= respiratory_rate <= 11:
        score += 1
    elif 12 <= respiratory_rate <= 20:
        score += 0
    elif 21 <= respiratory_rate <= 24:
        score += 2
    elif respiratory_rate >= 25:
        score += 3

    spo2 = float(measurement_data.get("spo2", 0))
    if spo2 <= 91:
        score += 3
    elif 92 <= spo2 <= 93:
        score += 2
    elif 94 <= spo2 <= 95:
        score += 1
    elif spo2 >= 96:
        score += 0

    systolic_bp = float(measurement_data.get("systolic_bp", 0))
    if systolic_bp <= 90:
        score += 3
    elif 91 <= systolic_bp <= 100:
        score += 2
    elif 101 <= systolic_bp <= 110:
        score += 1
    elif 111 <= systolic_bp <= 219:
        score += 0
    elif systolic_bp >= 220:
        score += 3

    heart_rate = float(measurement_data.get("heart_rate", 0))
    if heart_rate <= 40:
        score += 3
    elif 41 <= heart_rate <= 50:
        score += 1
    elif 51 <= heart_rate <= 90:
        score += 0
    elif 91 <= heart_rate <= 110:
        score += 1
    elif 111 <= heart_rate <= 130:
        score += 2
    elif heart_rate >= 131:
        score += 3

    temperature = float(measurement_data.get("temperature", 0))
    if temperature <= 35.0:
        score += 3
    elif 35.1 <= temperature <= 36.0:
        score += 1
    elif 36.1 <= temperature <= 38.0:
        score += 0
    elif 38.1 <= temperature <= 39.0:
        score += 1
    elif temperature >= 39.1:
        score += 2

    return score


def evaluate_measurement(measurement_data):
    """
    Evaluate a measurement dict against clinical thresholds.
    Returns: overall status, anomalies, news2 score
    """
    overall_status = "normal"
    anomalies = []
    news2_score = calculate_news2(measurement_data)

    for vital, value in measurement_data.items():
        val = float(value)
        thresholds = THRESHOLDS[vital]
        name = DISPLAY_NAMES.get(vital, vital)

        for severity in ("critical", "warning"):
            limits = thresholds[severity]
            low = limits[0]
            high = limits[1] if len(limits) > 1 else float("inf")

            if val <= low or val >= high:
                direction = "Low" if val <= low else "High"
                anomalies.append({
                    "vital_sign": vital,
                    "severity": severity,
                    "message": f"{direction} {name} ({val})",
                    "value": val,
                    "threshold": low if val <= low else high,
                })

                break  # critical found, skip warning for this vital

        for anomaly in anomalies:
            if anomaly["severity"] == "critical":
                overall_status = "critical"
            elif anomaly["severity"] == "warning" and overall_status != "critical":
                overall_status = "warning"

    return overall_status, anomalies, news2_score
