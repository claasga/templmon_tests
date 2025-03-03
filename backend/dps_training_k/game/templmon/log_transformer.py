import game.models.log_entry as le
from .signature_mapping import *

max_posix_timestamp = pow(2, 31) - 1


class MonpolyLogEntry:
    PERSONNEL_ARRIVED = "personnel_arrived"
    ASSIGNED_PERSONNEL = "assigned_personnel"
    UNASSIGNED_PERSONNEL = "unassigned_personnel"
    ASSIGNED_MATERIAL = "assigned_material"
    UNASSIGNED_MATERIAL = "unassigned_material"
    PATIENT_ARRIVED = "patient_arrived"
    CHANGED_STATE = "changed_state"
    UNKNOW_LOG_TYPE = "unknown_log_type"
    EXAMINATION_RESULT = "examination_result"
    ACTION_STARTED = "action_started"
    ACTION_CANCELED = "action_canceled"
    TRIAGED = "triage"
    COMMIT = "commit"


class LogTransformer:
    @classmethod
    def determine_log_type(cls, log_entry: le.LogEntry):
        l_types = le.LogEntry.TYPES
        l_categories = le.LogEntry.CATEGORIES
        if log_entry.category == l_categories.PERSONNEL and log_entry.type in [
            l_types.ARRIVED,
            l_types.ASSIGNED,
            l_types.UNASSIGNED,
        ]:
            if log_entry.type == l_types.ARRIVED:
                return MonpolyLogEntry.PERSONNEL_ARRIVED
            elif log_entry.type == l_types.ASSIGNED:
                return MonpolyLogEntry.ASSIGNED_PERSONNEL
            elif log_entry.type == l_types.UNASSIGNED:
                return MonpolyLogEntry.UNASSIGNED_PERSONNEL
        elif log_entry.category == l_categories.PATIENT and log_entry.type in [
            l_types.ARRIVED,
            l_types.UPDATED,
            l_types.TRIAGED,
        ]:
            if log_entry.type == l_types.ARRIVED:
                return MonpolyLogEntry.PATIENT_ARRIVED
            elif log_entry.type == l_types.UPDATED:
                return MonpolyLogEntry.CHANGED_STATE
            elif log_entry.type == l_types.TRIAGED:
                return MonpolyLogEntry.TRIAGED
        elif log_entry.category == l_categories.ACTION and log_entry.type in [
            l_types.FINISHED,
            l_types.STARTED,
            l_types.CANCELED,
        ]:
            if (
                log_entry.type == l_types.FINISHED
                and "examination_result" in log_entry.content
            ):
                return MonpolyLogEntry.EXAMINATION_RESULT
            elif log_entry.type == l_types.STARTED:
                return MonpolyLogEntry.ACTION_STARTED
            elif log_entry.type == l_types.CANCELED:
                return MonpolyLogEntry.ACTION_CANCELED
        elif log_entry.category == l_categories.MATERIAL and log_entry.type in [
            l_types.ASSIGNED,
            l_types.UNASSIGNED,
        ]:
            if log_entry.type == l_types.ASSIGNED:
                return MonpolyLogEntry.ASSIGNED_MATERIAL
            elif log_entry.type == l_types.UNASSIGNED:
                return MonpolyLogEntry.UNASSIGNED_MATERIAL
        else:
            return MonpolyLogEntry.UNKNOW_LOG_TYPE

    @classmethod
    def trigger_event(cls, posix_timestamp):
        return f"@{posix_timestamp} trigger_event()"

    @classmethod
    def _generate_timestamp(cls, log_entry: le.LogEntry):
        return str(log_entry.timestamp.timestamp())

    @classmethod
    def transform(cls, log_entry: le.LogEntry):
        log_type = cls.determine_log_type(log_entry)
        timestamp = cls._generate_timestamp(log_entry)
        log_str = f"@{timestamp} "

        if log_type == MonpolyLogEntry.ASSIGNED_PERSONNEL:
            personnel_id = log_entry.personnel.all().first().pk
            patient_id = log_entry.patient_instance.pk
            log_str += AssignedPersonnel.log(personnel_id, patient_id)

        elif log_type == MonpolyLogEntry.UNASSIGNED_PERSONNEL:
            personnel_id = log_entry.personnel.all().first().pk
            log_str += UnassignedPersonnel.log(
                personnel_id,
            )

        elif log_type == MonpolyLogEntry.PATIENT_ARRIVED:
            patient_id = log_entry.patient_instance.pk
            area_id = log_entry.area.pk
            triage_display = log_entry.patient_instance.get_triage_display()
            injuries = log_entry.content.get("injuries", "")
            log_str += PatientArrived.log(patient_id, area_id, triage_display, injuries)
        elif log_type == MonpolyLogEntry.CHANGED_STATE:
            patient_id = log_entry.patient_instance.pk
            airway = log_entry.content.get("state", {}).get("Airway", "")
            circulation = log_entry.content.get("state", {}).get("Circulation", "")
            dead = log_entry.content.get("dead")
            log_str += ChangedState.log(patient_id, airway, circulation, dead)
        elif log_type == MonpolyLogEntry.ACTION_STARTED:
            patient_id = log_entry.patient_instance.pk
            action = log_entry.content.get("name")
            log_str += ActionStarted.log(patient_id, action)
        elif log_type == MonpolyLogEntry.ACTION_CANCELED:
            patient_id = log_entry.patient_instance.pk
            action = log_entry.content.get("name")
            log_str += ActionCanceled.log(patient_id, action)
        elif log_type == MonpolyLogEntry.EXAMINATION_RESULT:
            patient_id = log_entry.patient_instance.pk
            action = log_entry.content.get("name")
            result = log_entry.content.get("examination_result")
            log_str += ExaminationResult.log(patient_id, action, result)
        elif log_type == MonpolyLogEntry.TRIAGED:
            patient_id = log_entry.patient_instance.pk
            level = log_entry.content.get("level")
            log_str += Triaged.log(patient_id, level)
        elif log_type == MonpolyLogEntry.ASSIGNED_MATERIAL:
            material_id = log_entry.materials.all().first().pk
            patient_id = log_entry.patient_instance.pk
            log_str += AssignedMaterial.log(material_id, patient_id)
        elif log_type == MonpolyLogEntry.UNASSIGNED_MATERIAL:
            material_id = log_entry.materials.all().first().pk
            log_str += UnassignedMaterial.log(material_id)
        else:
            log_str += f"unknown_log_type({log_entry.pk}, {log_entry.type}, {log_entry.category})"

        return log_str

    @classmethod
    def generate_commit(cls, transformed_log_entry: str):
        return transformed_log_entry[: transformed_log_entry.find(" ")] + " commit()"
