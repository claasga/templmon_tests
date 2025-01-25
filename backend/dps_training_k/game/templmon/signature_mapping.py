class SignatureMapper:
    def __init__(self, types, default_names=None):
        self.types = types
        if not default_names:
            default_names = self.types
        self.default_names = default_names


class RuleProperty:
    LOCATION = "location"
    PERSONNEL = "personnel"
    PATIENT = "patient"
    ACTION = "action"
    RESULT = "result"
    DEVICE = "device"
    TRIAGE = "triage"
    INJURY_LEVEL = "injury_level"
    AIRWAY = "airway"
    BREATHING = "breathing"
    CIRCULATION = "circulation"
    BEWUSSTSEIN = "consciousness"
    PUPILLEN = "pupils"
    PSYCHE = "psyche"
    HAUT = "skin"
    ALIVENESS = "aliveness"
    UNKNOWN = "unknown"


RP = RuleProperty
assigned_personnel = SignatureMapper([RP.PERSONNEL, RP.PATIENT])
unassigned_personnel = SignatureMapper([RP.PERSONNEL])
changed_state = SignatureMapper([RP.PATIENT, RP.AIRWAY, RP.CIRCULATION, RP.ALIVENESS])
patient_arrived = SignatureMapper([RP.PATIENT, RP.LOCATION, RP.INJURY_LEVEL, RP.TRIAGE])
patient_relocated = SignatureMapper(
    [RP.PATIENT, RP.LOCATION, RP.LOCATION],
    [RP.PATIENT, f"{RP.LOCATION}_old", f"{RP.LOCATION}_new"],
)
