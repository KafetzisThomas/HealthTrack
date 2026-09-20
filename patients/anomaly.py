
THRESHOLDS = {
    # MEDICAL SOURCES
    # ---------------
    # National Early Warning Score 2 (NEWS2): https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf
    # American Heart Association (AHA): https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings

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
