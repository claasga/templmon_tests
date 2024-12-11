import game.models.log_entry as le
import datetime

max_posix_timestamp = pow(2, 31) - 1


class MonpolyLogEntry:
    PERSONNEL_ARRIVED = "personnel_arrived"
    ASSIGNED_PERSONNEL = "assigned_personnel"
    UNASSIGNED_PERSONNEL = "unassigned_personnel"
    PATIENT_ARRIVED = "patient_arrived"
    UNKNOW_LOG_TYPE = "unknown_log_type"


def determine_log_type(log_entry: le.LogEntry):
    if log_entry.category == le.LogEntry.CATEGORIES.PERSONNEL:
        if log_entry.type == le.LogEntry.TYPES.ARRIVED:
            return MonpolyLogEntry.PERSONNEL_ARRIVED
        elif log_entry.type == le.LogEntry.TYPES.ASSIGNED:
            return MonpolyLogEntry.ASSIGNED_PERSONNEL
        elif log_entry.type == le.LogEntry.TYPES.UNASSIGNED:
            return MonpolyLogEntry.UNASSIGNED_PERSONNEL
    elif log_entry.category == le.LogEntry.CATEGORIES.PATIENT:
        if log_entry.type == le.LogEntry.TYPES.ARRIVED:
            return MonpolyLogEntry.PATIENT_ARRIVED
    else:
        return MonpolyLogEntry.UNKNOW_LOG_TYPE


def trigger_event(posix_timestamp):
    return f"@{posix_timestamp} trigger_event()"


def generate_timestamp(log_entry: le.LogEntry):
    return str(log_entry.timestamp.timestamp())


def transform(log_entry: le.LogEntry):
    log_type = determine_log_type(log_entry)
    timestamp = generate_timestamp(log_entry)
    log_str = f"@{timestamp} "

    if log_type == MonpolyLogEntry.ASSIGNED_PERSONNEL:
        personnel_id = log_entry.personnel.all().first().pk
        patient_id = log_entry.patient_instance.pk
        log_str += f"assigned_personnel({personnel_id}, {patient_id})"

    elif log_type == MonpolyLogEntry.UNASSIGNED_PERSONNEL:
        personnel_id = log_entry.personnel.all().first().pk
        log_str += f"unassigned_personnel({personnel_id})"

    elif log_type == MonpolyLogEntry.PATIENT_ARRIVED:
        patient_id = log_entry.patient_instance.pk
        area_id = log_entry.area.pk
        triage_display = log_entry.patient_instance.get_triage_display()
        injuries = f'"{log_entry.content["injuries"]}"'
        log_str += (
            f"patient_arrived({patient_id}, {area_id}, {triage_display}, {injuries})"
        )
    else:
        log_str += f"unknown_log_type({log_entry.pk})"

    return log_str
