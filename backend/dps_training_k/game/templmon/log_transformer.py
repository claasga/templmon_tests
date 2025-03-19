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
    start_time = None

    @classmethod
    def determine_log_type(cls, log_entry: le.LogEntry):
        l_types = le.LogEntry.TYPES
        l_categories = le.LogEntry.CATEGORIES
        mapping = {
            (
                l_categories.PERSONNEL,
                l_types.ARRIVED,
            ): MonpolyLogEntry.PERSONNEL_ARRIVED,
            (
                l_categories.PERSONNEL,
                l_types.ASSIGNED,
            ): MonpolyLogEntry.ASSIGNED_PERSONNEL,
            (
                l_categories.PERSONNEL,
                l_types.UNASSIGNED,
            ): MonpolyLogEntry.UNASSIGNED_PERSONNEL,
            (l_categories.PATIENT, l_types.ARRIVED): MonpolyLogEntry.PATIENT_ARRIVED,
            (l_categories.PATIENT, l_types.UPDATED): MonpolyLogEntry.CHANGED_STATE,
            (l_categories.PATIENT, l_types.TRIAGED): MonpolyLogEntry.TRIAGED,
            (l_categories.ACTION, l_types.STARTED): MonpolyLogEntry.ACTION_STARTED,
            (l_categories.ACTION, l_types.CANCELED): MonpolyLogEntry.ACTION_CANCELED,
            (
                l_categories.MATERIAL,
                l_types.ASSIGNED,
            ): MonpolyLogEntry.ASSIGNED_MATERIAL,
            (
                l_categories.MATERIAL,
                l_types.UNASSIGNED,
            ): MonpolyLogEntry.UNASSIGNED_MATERIAL,
        }
        key = (log_entry.category, log_entry.type)
        if key == (l_categories.ACTION, l_types.FINISHED):
            return (
                MonpolyLogEntry.EXAMINATION_RESULT
                if "examination_result" in log_entry.content
                else MonpolyLogEntry.UNKNOW_LOG_TYPE
            )
        return mapping.get(key, MonpolyLogEntry.UNKNOW_LOG_TYPE)

    @classmethod
    def trigger_event(cls, posix_timestamp):
        return f"@{posix_timestamp} trigger_event()"

    @classmethod
    def _generate_timestamp(cls, log_entry: le.LogEntry):
        return str(
            int(
                (log_entry.timestamp.timestamp() - cls.start_time.timestamp()) * 1000000
            )
        )

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
            breathing = log_entry.content.get("state", {}).get("Breathing", "")
            # print(f"LT: Breathing is {breathing}")
            breathing = (
                int(
                    "".join(
                        filter(str.isdigit, breathing[: str(breathing).find("/min")])
                    )
                )
                if breathing
                else "0"
            )
            circulation = log_entry.content.get("state", {}).get("Circulation", "")
            # print(f"LT: Circulation is {circulation}")

            circulation = (
                int(
                    "".join(
                        filter(
                            str.isdigit, circulation[: str(circulation).find("/min")]
                        )
                    )
                )
                if circulation
                else "0"
            )
            dead = log_entry.content.get("dead")
            log_str += ChangedState.log(patient_id, circulation, breathing, dead)
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
