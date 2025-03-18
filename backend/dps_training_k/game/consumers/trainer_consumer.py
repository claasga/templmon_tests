import time
from urllib.parse import parse_qs
from collections import defaultdict
from datetime import datetime
from configuration import settings
from game.models import Area
from game.models import Exercise, Personnel, PatientInstance, MaterialInstance, LogEntry
from game.models import Lab
from template.constants import MaterialIDs
from template.models import PatientInformation, Material
from .abstract_consumer import AbstractConsumer
from . import patient_consumer
from ..channel_notifications import (
    ChannelNotifier,
    LogEntryDispatcher,
    ViolationDispatcher,
)
from ..serializers import LogEntrySerializer
from ..templmon.rule_generators import *
from ..templmon.rule_runner import RuleRunner, InvalidFormulaError
import os
import json


class TrainerConsumer(AbstractConsumer):
    """
    for general functionality @see AbstractConsumer
    """

    class TrainerIncomingMessageTypes:
        AREA_ADD = "area-add"
        AREA_DELETE = "area-delete"
        AREA_RENAME = "area-rename"
        EXAMPLE = "example"
        EXERCISE_CREATE = "exercise-create"
        EXERCISE_END = "exercise-end"
        EXERCISE_START = "exercise-start"
        MATERIAL_ADD = "material-add"
        MATERIAL_DELETE = "material-delete"
        PATIENT_ADD = "patient-add"
        PATIENT_DELETE = "patient-delete"
        PATIENT_RENAME = "patient-rename"
        PATIENT_UPDATE = "patient-update"
        PERSONNEL_ADD = "personnel-add"
        PERSONNEL_DELETE = "personnel-delete"
        PERSONNEL_RENAME = "personnel-rename"
        LOG_RULE_ADD = "log-rule-add"
        LOG_RULE_DELETE = "log-rule-delete"

    class TrainerOutgoingMessageTypes:
        LOG_UPDATE = "log-update"
        RESPONSE = "response"
        TRAINER_MEASUREMENT_FINISHED = "trainer-measurement-finished"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_arguments = [
            lambda: (
                Exercise.objects.get(frontend_id=self.exercise_frontend_id)
                if self.exercise_frontend_id
                else None
            )
        ]
        self.patient_instances_latencies = defaultdict(list)
        self.exercise_frontend_id = None
        self.exercise = None
        self.rules_count = 0
        self.received_rules_count = 0
        trainer_request_map = {
            self.TrainerIncomingMessageTypes.AREA_ADD: (self.handle_add_area,),
            self.TrainerIncomingMessageTypes.AREA_DELETE: (
                self.handle_delete_area,
                "areaId",
            ),
            self.TrainerIncomingMessageTypes.AREA_RENAME: (
                self.handle_rename_area,
                "areaId",
                "areaName",
            ),
            self.TrainerIncomingMessageTypes.EXAMPLE: (
                self.handle_example,
                "exerciseId",
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_CREATE: (
                self.handle_create_exercise,
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_END: (self.handle_end_exercise,),
            self.TrainerIncomingMessageTypes.EXERCISE_START: (
                self.handle_start_exercise,
            ),
            self.TrainerIncomingMessageTypes.MATERIAL_ADD: (
                self.handle_add_material,
                "areaId",
                "materialName",
            ),
            self.TrainerIncomingMessageTypes.MATERIAL_DELETE: (
                self.handle_delete_material,
                "materialId",
            ),
            self.TrainerIncomingMessageTypes.PATIENT_ADD: (
                self.handle_add_patient,
                "areaId",
                "patientName",
                "code",
            ),
            self.TrainerIncomingMessageTypes.PATIENT_DELETE: (
                self.handle_delete_patient,
                "patientId",
            ),
            self.TrainerIncomingMessageTypes.PATIENT_RENAME: (
                self.handle_rename_patient,
                "patientId",
                "patientName",
            ),
            self.TrainerIncomingMessageTypes.PATIENT_UPDATE: (
                self.handle_update_patient,
                "patientId",
                "code",
            ),
            self.TrainerIncomingMessageTypes.PERSONNEL_ADD: (
                self.handle_add_personnel,
                "areaId",
                "personnelName",
            ),
            self.TrainerIncomingMessageTypes.PERSONNEL_DELETE: (
                self.handle_delete_personnel,
                "personnelId",
            ),
            self.TrainerIncomingMessageTypes.PERSONNEL_RENAME: (
                self.handle_rename_personnel,
                "personnelId",
                "personnelName",
            ),
            self.TrainerIncomingMessageTypes.LOG_RULE_ADD: (
                self.handle_add_rule,
                "type",
                "name",
                "configuration",
            ),
            self.TrainerIncomingMessageTypes.LOG_RULE_DELETE: (
                self.handle_delete_log_rule,
                "logRuleId",
            ),
        }
        self.REQUESTS_MAP.update(trainer_request_map)

    def connect(self):
        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        success, _ = self.authenticate(token)
        if success:
            self.accept()
            self.send_available_patients()
            self.send_available_materials()
            if self.exercise:
                self.send_past_logs()
        self.directory_path = os.path.join(
            self.MEASUREMENTS_DIRECTORY,
            f"measurements_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
        )
        os.makedirs(self.directory_path, mode=0o755, exist_ok=True)

    def save_measurements(self):
        print(f"TC: saving measurements: {self.patient_instances_latencies}")

        file_path = os.path.join(self.directory_path, "trainer_latencies.json")
        print(f"TC: file path: {file_path}")
        with open(file_path, "w") as f:
            json.dump(self.patient_instances_latencies, f, default=list)
        os.chmod(file_path, 0o666)
        print(f"TC: saved measurements to {file_path}")

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    # API Methods, open to client.
    # These methods are not allowed to be called directly. If you want to call them from the backend, go via self.receive_json()
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def handle_add_area(self, exercise):
        Area.create_area(name="Bereich", exercise=exercise, isPaused=False)

    def handle_add_rule(self, exercise, type, name, configuration):
        rule_generators = {
            "symptom_combination": SymptomCombinationRule.generate,
            "personnel_check": PersonnelCheckRule.generate,
            "personnel_prioritization": PersonnelPrioritizationRule.generate,
            "triage_goal": TriageGoalRule.generate,
            "aliveness_check": AlivenessChecker.generate,
            "interacted_check": InteractedChecker.generate,
            "triaged_check": TriagedChecker.generate,
            "berlin_algorithm": BerlinAlgorithm.generate,
        }

        try:
            if type in rule_generators:
                rules = rule_generators[type](name, **configuration)
                if not isinstance(rules, list):
                    rules = [rules]
            else:
                self.send_failure(f"Unknown rule type '{type}'")
                return
            for rule in rules:
                RuleRunner(exercise.frontend_id, LogEntryDispatcher, rule)
                self.rules_count += 1
        except InvalidFormulaError as e:
            self.send_failure(str(e))

    def handle_delete_area(self, _, areaId):
        try:
            area = Area.objects.get(id=areaId)
            area.delete()
        except Area.DoesNotExist:
            self.send_failure(
                f"No area found with the id '{areaId}'",
            )

    def handle_rename_area(self, exercise, area_id, area_name):
        area = Area.objects.get(id=area_id, exercise_id=exercise.id)
        area.name = area_name
        area.save(update_fields=["name"])

    def handle_example(self, exercise, exercise_frontend_id):
        self.exercise_frontend_id = exercise_frontend_id
        self.send_event(
            self.TrainerOutgoingMessageTypes.RESPONSE,
            content=f"exerciseId {self.exercise_frontend_id}",
        )

    # here, the exercise argument is None
    def handle_create_exercise(self, exercise):
        if Exercise.objects.filter(trainer=self.user).exists():
            self.exercise = Exercise.objects.get(trainer=self.user)
        else:
            self.exercise = Exercise.createExercise(self.user)
        self.exercise_frontend_id = self.exercise.frontend_id
        Lab.objects.get(exercise=self.exercise).create_basic_devices()
        self._send_exercise(self.exercise)
        self.subscribe(ChannelNotifier.get_group_name(self.exercise))
        self.subscribe(LogEntryDispatcher.get_group_name(self.exercise))
        self.subscribe(ViolationDispatcher.get_group_name(self.exercise.frontend_id))

        # content = {"operator": "<", "personnel_count": 2}
        # self.handle_add_rule(self.exercise, "personnel_check", "less_two_rule", content

    def handle_end_exercise(self, exercise):
        print(
            """TC: ********************
        attention******************
        the  end exercise method is called
        """
        )
        exercise.update_state(Exercise.StateTypes.FINISHED)

    def handle_start_exercise(self, exercise):
        exercise.start_exercise()

    def handle_add_material(self, _, areaId, materialName):
        try:
            area = Area.objects.get(id=areaId)
            template = Material.objects.get(name=materialName)
            MaterialInstance.objects.create(template=template, area=area)
        except Area.DoesNotExist:
            self.send_failure(
                f"No area found with the id '{areaId}'",
            )
        except Area.MultipleObjectsReturned:
            self.send_failure(
                f"Multiple areas found with the id '{areaId}'",
            )

    def handle_delete_material(self, _, materialId):
        try:
            material = MaterialInstance.objects.get(id=materialId)
            if not material.patient_instance:
                material.delete()
            else:
                self.send_failure(
                    "Material ist einem Patienten zugewiesen und kann deswegen nicht gelöscht werden. Bitte gebe zuerst das Material frei oder "
                    "lösche den Patienten."
                )
        except MaterialInstance.DoesNotExist:
            self.send_failure(
                f"No material found with the id '{materialId}'",
            )

    def handle_add_patient(self, _, areaId, patientName, code):
        try:
            area = Area.objects.get(id=areaId)
            patient_information = PatientInformation.objects.get(code=code)
            # a patient in state 551 starts "beatmet" and therefore needs a "Beatmungsgerät"
            if patient_information.start_status == 551:
                try:
                    material_instances = MaterialInstance.objects.filter(
                        template__uuid__in=[
                            MaterialIDs.BEATMUNGSGERAET_TRAGBAR,
                            MaterialIDs.BEATMUNGSGERAET_STATIONAER,
                        ]
                    )
                    # find a "Beatmungsgerät" that has not been assigned to a patient but is in same area as the patient
                    succeeded = False
                    for material_instance in material_instances:
                        if material_instance.attached_instance() == area:
                            succeeded = True
                            break

                    if succeeded:
                        patient_instance = PatientInstance.objects.create(
                            name=patientName,
                            static_information=patient_information,
                            exercise=area.exercise,
                            area=area,
                            frontend_id=settings.ID_GENERATOR.get_patient_frontend_id(),
                        )
                        material_instance.try_moving_to(patient_instance)
                    else:  # catches case where no material_instance was in patients area
                        self.send_failure(
                            message="Dieser Patient benötigt bereits zu Beginn ein Beatmungsgerät."
                        )
                except (
                    MaterialInstance.DoesNotExist
                ):  # catches no material_instance matching filter
                    self.send_failure(
                        message="Dieser Patient benötigt bereits zu Beginn ein Beatmungsgerät."
                    )
            else:
                PatientInstance.objects.create(
                    name=patientName,
                    static_information=patient_information,
                    exercise=area.exercise,
                    area=area,
                    frontend_id=settings.ID_GENERATOR.get_patient_frontend_id(),
                )

        except Area.DoesNotExist:
            self.send_failure(
                f"No area found with the id '{areaId}'",
            )
        except Area.MultipleObjectsReturned:
            self.send_failure(
                f"Multiple areas found with the id '{areaId}'",
            )

    def handle_delete_patient(self, _, patientFrontendId):
        try:
            patient = PatientInstance.objects.get(frontend_id=patientFrontendId)
            if patient.static_information.start_status == 551:
                self._unassign_beatmungsgeraet(patient)
            patient.delete()

        except PatientInstance.DoesNotExist:
            self.send_failure(
                f"No patient found with the patientId '{patientFrontendId}'",
            )

    def handle_rename_patient(self, exercise, patient_id, patient_name):
        patient = PatientInstance.objects.get(
            frontend_id=patient_id, exercise_id=exercise.id
        )
        patient.name = patient_name
        patient.save(update_fields=["name"])

    def handle_update_patient(self, _, patient_frontend_id, code):
        patient = PatientInstance.objects.get(frontend_id=patient_frontend_id)
        new_patient_information = PatientInformation.objects.get(code=code)
        if patient.static_information.start_status == 551:
            self._unassign_beatmungsgeraet(patient)

        # if new start state is 551, try to assign a "Beatmungsgerät"
        if new_patient_information.start_status == 551:
            try:
                ventilators = MaterialInstance.objects.filter(
                    template__uuid__in=[
                        MaterialIDs.BEATMUNGSGERAET_TRAGBAR,
                        MaterialIDs.BEATMUNGSGERAET_STATIONAER,
                    ]
                )
                # find a "Beatmungsgerät" that has not been assigned to a patient but is in same area as the patient
                succeeded = False
                for ventilator in ventilators:
                    if ventilator.attached_instance() == patient.area:
                        succeeded = True
                        break
                if succeeded:
                    patient.static_information = new_patient_information
                    patient.save(update_fields=["static_information"])
                    # While Python does know the concept of scopes, one can still use the variables after the for loop. So what happens here is that
                    # the for loop loops until it finds a desired ventilator and then breaks as to not overwrite the current instance.
                    ventilator.try_moving_to(patient)
                else:
                    self.send_failure(
                        message="Dieser Patient benötigt bereits zu Beginn ein Beatmungsgerät."
                    )

            except:
                self.send_failure(
                    message="Dieser Patient benötigt bereits zu Beginn ein Beatmungsgerät."
                )
        else:
            patient.static_information = new_patient_information
            patient.save(update_fields=["static_information"])

    def handle_add_personnel(self, _, areaId, personnel_name):
        try:
            area = Area.objects.get(id=areaId)
            Personnel.create_personnel(area=area, name=personnel_name)
        except Area.DoesNotExist:
            self.send_failure(
                f"No area found with the id '{areaId}'",
            )
        except Area.MultipleObjectsReturned:
            self.send_failure(
                f"Multiple areas found with the id '{areaId}'",
            )

    def handle_delete_personnel(self, _, personnel_id):
        try:
            personnel = Personnel.objects.get(id=personnel_id)
            if not personnel.patient_instance:
                personnel.delete()
            else:
                self.send_failure(
                    "Personal ist einem Patienten zugewiesen und kann deswegen nicht gelöscht werden. Bitte gebe zuerst das Personal frei oder "
                    "lösche den Patienten."
                )
        except Personnel.DoesNotExist:
            self.send_failure(
                f"No personnel found with the id '{personnel_id}'",
            )

    def handle_rename_personnel(self, _, personnel_id, personnel_name):
        personnel = Personnel.objects.get(id=personnel_id)
        personnel.name = personnel_name
        personnel.save(update_fields=["name"])

    def handle_delete_log_rule(self, _, log_rule_id):
        pass

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    # methods used internally
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def send_past_logs(self, exercise):
        log_entry_objects = LogEntry.objects.filter(exercise=exercise)
        log_entry_objects = filter(
            lambda log_entry: log_entry.is_valid(), log_entry_objects
        )
        if not log_entry_objects:
            return
        log_entry_dicts = [
            LogEntrySerializer(log_entry).data for log_entry in log_entry_objects
        ]
        self.send_event(
            self.TrainerOutgoingMessageTypes.LOG_UPDATE, logEntries=log_entry_dicts
        )

    def _unassign_beatmungsgeraet(self, patient):
        material_instances = MaterialInstance.objects.filter(
            template__uuid__in=[
                MaterialIDs.BEATMUNGSGERAET_TRAGBAR,
                MaterialIDs.BEATMUNGSGERAET_STATIONAER,
            ]
        )
        # find the "Beatmungsgerät" that has been assigned to the patient
        for material_instance in material_instances:
            if material_instance.attached_instance() == patient:
                break
        # unassign "Beatmungsgerät"
        material_instance.try_moving_to(patient.area)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    # Events triggered internally by channel notifications
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def log_update_event(self, event):
        return
        log_entry = LogEntry.objects.get(id=event["log_entry_id"])
        self.send_event(
            self.TrainerOutgoingMessageTypes.LOG_UPDATE,
            logEntries=[LogEntrySerializer(log_entry).data],
        )

    def singular_violation_event(self, event):
        print("Singular violation event")
        print(event)

    def durational_violation_start_event(self, event):
        print("Durational violation start event")
        print(event)

    def durational_violation_end_event(self, event):
        print("Durational violation end event")
        print(event)

    def durational_violation_update_event(self, event):
        print("Durational violation update event")
        print(event)

    def violation_processing_finished_event(self, event):
        if self.closed:
            print("Violation processing skipped, as the connection is already closed.")
            return
        current_time = time.perf_counter()
        logtype = event["input_type"]
        rule_id = f'{event["template_name"]}_{event["rule_name"]}'
        monpoly_measuring_start = float(event["monpoly_measuring_start"])
        monpoly_measuring_end = float(event["monpoly_measuring_end"])
        print(
            f"TC: measured_logtype == {patient_consumer.measuring_instance.measured_logtype if patient_consumer.measuring_instance else None}"
        )
        if not patient_consumer.measuring_instance:
            return
        measured_logtype = patient_consumer.measuring_instance.measured_logtype
        currently_tested_patient = (
            patient_consumer.measuring_instance.patient_frontend_id
        )
        measurement_start = patient_consumer.measuring_instance.measurement_start
        print(f"TC: own logtype = {logtype}, fetched logtype = {measured_logtype}")
        if logtype != measured_logtype:
            return

        self.received_rules_count += 1
        if self.received_rules_count == 1:
            self.patient_instances_latencies[currently_tested_patient].append({})

        self.patient_instances_latencies[currently_tested_patient][-1][rule_id] = (
            current_time,
            current_time - measurement_start,
            current_time - monpoly_measuring_start,
            monpoly_measuring_end - monpoly_measuring_start,
        )
        # print(f"TC: current measurments: {self.patient_instances_latencies}")
        print(
            f"TC: measured time: {self.patient_instances_latencies[currently_tested_patient][-1]}"
        )
        if self.received_rules_count == self.rules_count:
            self.received_rules_count = 0
            patient_consumer.measuring_instance.finish_measurement()
            self.send_event(
                self.TrainerOutgoingMessageTypes.TRAINER_MEASUREMENT_FINISHED
            )
