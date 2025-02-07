from django.db import models
from django.utils import timezone

from game.channel_notifications import LogEntryDispatcher


class LogEntry(models.Model):
    class CATEGORIES(models.TextChoices):
        ACTION = "AC", "action"
        EXERCISE = "EX", "exercise"
        MATERIAL = "MA", "material"
        PERSONNEL = "PE", "personnel"
        PATIENT = "PA", "patient"

    class TYPES(models.TextChoices):
        ARRIVED = "AR", "arrived"
        ASSIGNED = "AS", "assigned"
        UNASSIGNED = "UA", "unassigned"
        STARTED = "ST", "started"
        FINISHED = "FI", "finished"
        CANCELED = "CA", "canceled"
        IN_EFFECT = "IE", "in effect"
        EXPIRED = "EX", "expired"
        MOVED = "MO", "moved"
        TRIAGED = "TR", "triaged"
        UPDATED = "UP", "updated"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["local_id", "exercise"], name="unique_local_id_for_entry"
            )
        ]

    local_id = models.IntegerField(blank=True)
    exercise = models.ForeignKey("Exercise", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        null=True, blank=True, help_text="May only be set while exercise is running"
    )
    category = models.CharField(
        choices=CATEGORIES.choices, max_length=2, blank=True, null=True
    )  # need to remove blank and null when production
    type = models.CharField(
        choices=TYPES.choices, max_length=2, blank=True, null=True
    )  # need to remove blank and null when production
    content = models.JSONField(blank=True, null=True, default=None)
    is_dirty = models.BooleanField(
        default=False,
        help_text="Set to True if objects is missing relevant Keys (e.g. timestamp)",
    )

    patient_instance = models.ForeignKey(
        "PatientInstance", on_delete=models.CASCADE, null=True, blank=True
    )
    area = models.ForeignKey("Area", on_delete=models.CASCADE, null=True, blank=True)
    materials = models.ManyToManyField("MaterialInstance", blank=True)
    personnel = models.ManyToManyField("Personnel", blank=True)

    @property
    def message(self):
        return self._verbosify_content(self.content)

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.exercise.is_running():
                self.timestamp = timezone.now()
            else:
                self.timestamp = None

            self.local_id = self.generate_local_id(
                self.exercise
            )  # prone to race conditions

        changes = kwargs.get("update_fields", None)
        LogEntryDispatcher.save_and_notify(self, changes, super(), *args, **kwargs)

    @classmethod
    def set_empty_timestamps(cls, exercise):
        log_entries = cls.objects.filter(exercise=exercise, timestamp=None)
        current_timestamp = timezone.now()
        for log_entry in log_entries:
            log_entry.timestamp = current_timestamp
            log_entry.save(update_fields=["timestamp"])
        return log_entries

    def generate_local_id(self, exercise):
        highest_local_id = LogEntry.objects.filter(exercise=exercise).aggregate(
            models.Max("local_id")
        )["local_id__max"]
        if highest_local_id:
            return highest_local_id + 1
        return 1

    def is_valid(self):
        if self.timestamp and self.local_id and not self.is_dirty:
            return True
        # print("not valid")
        return False

    def set_dirty(self, new_dirty):
        self.is_dirty = new_dirty
        self.save(update_fields=["is_dirty"])

    def _verbosify_content(self, content):
        if not content:
            return ""
        message = ""
        type_to_submessage = {
            self.TYPES.ARRIVED: "ist erschienen",
            self.TYPES.ASSIGNED: "wurde zugewiesen",
            self.TYPES.UNASSIGNED: "wurde freigegeben",
            self.TYPES.STARTED: "wurde gestartet",
            self.TYPES.FINISHED: "wurde abgeschlossen",
            self.TYPES.CANCELED: "wurde abgebrochen",
            self.TYPES.IN_EFFECT: "beginnt zu wirken",
            self.TYPES.EXPIRED: "wirkt nicht mehr",
            self.TYPES.MOVED: "wurde verlegt",
            self.TYPES.TRIAGED: "wurde triagiert",
            self.TYPES.UPDATED: "wurde aktualisiert",
        }
        if self.category == self.CATEGORIES.ACTION:
            message += f"{(content['name'])} {type_to_submessage[self.type]}"
            message += (
                ("und hat " + content["produced"] + " produziert")
                if "produced" in content
                else ""
            )
        elif self.category == self.CATEGORIES.EXERCISE:
            message += f"Übung {type_to_submessage[self.type]}"
        elif self.category == self.CATEGORIES.MATERIAL:
            message += f"{content['name']} {type_to_submessage[self.type]}"
            if self.type == self.TYPES.ASSIGNED:
                message += f" zu {content['location_type']} {content['location_name']}"
        elif self.category == self.CATEGORIES.PATIENT:
            type_to_submessage[self.TYPES.ARRIVED] = "wurde eingeliefert"
            type_to_submessage[self.TYPES.UPDATED] = "hat seinen Zustand gewechselt"
            print(f"Type is: {self.type}")
            message += f"Patient*in {content['name']}({content['code']}) {type_to_submessage[self.type]}"
            if "injuries" in content:
                message += f" mit den folgenden Verletzungen: {content['injuries']}"
            elif "level" in content:
                message += f" mit der Triage-Stufe {content['level']}"
            elif "location_category" in content:
                message += (
                    f" nach {content['location_type']} {content['location_name']}"
                )
            elif "state" in content:
                message += f" zu {content['state']}"
        elif self.category == self.CATEGORIES.PERSONNEL:
            type_to_submessage[self.TYPES.ARRIVED] = "ist eingetroffen"
            message += f"{content['name']} {type_to_submessage[self.type]}"
            if self.type == self.TYPES.ARRIVED:
                message += f" in {content['location_type']} {content['location_name']}"
            elif self.type == self.TYPES.ASSIGNED:
                message += f" zu {content['location_type']} {content['location_name']}"
        return message
