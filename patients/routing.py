from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/patient/<int:patient_id>/", consumers.PatientMonitorConsumer.as_asgi()),
    path("ws/dashboard/", consumers.DashboardConsumer.as_asgi()),
]
