from django.db import models
from .patient import Patient


class PatientState(models.Model):
    stateID = models.IntegerField(
        help_text="state number as it is used in original data set"
    )
    patientID = models.ForeignKey(Patient, on_delete=models.CASCADE)
    data = models.JSONField(help_text="data for patient in current phase")
    phase = models.IntegerField(help_text="current phase, e.g. 3")

    class Meta:
        unique_together = (
            "stateID",
            "patientID",
        )
