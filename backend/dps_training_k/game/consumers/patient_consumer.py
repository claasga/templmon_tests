from urllib.parse import parse_qs

from game.models import PatientInstance, Exercise, ActionInstanceStateNames
from template.serializer.state_serialize import StateSerializer
from .abstract_consumer import AbstractConsumer
from ..channel_notifications import ChannelNotifier


class PatientConsumer(AbstractConsumer):
    """
    for general functionality @see AbstractConsumer
    """

    class PatientIncomingMessageTypes:
        EXAMPLE = "example"
        TEST_PASSTHROUGH = "test-passthrough"
        TRIAGE = "triage"
        ACTION_ADD = "action-add"

    class PatientOutgoingMessageTypes:
        RESPONSE = "response"
        EXERCISE = "exercise"
        TEST_PASSTHROUGH = "test-passthrough"
        STATE_CHANGE = "state-change"
        ACTION_CONFIRMATION = "action-confirmation"
        ACTION_DECLINATION = "action-declination"
        ACTION_RESULT = "action-result"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_id = ""
        self.patient_instance = None
        self.REQUESTS_MAP = {
            self.PatientIncomingMessageTypes.EXAMPLE: (
                self.handle_example,
                "exercise_code",
                "patient_code",
            ),
            self.PatientIncomingMessageTypes.TEST_PASSTHROUGH: (
                self.handle_test_passthrough,
            ),
            self.PatientIncomingMessageTypes.TRIAGE: (
                self.handle_triage,
                "triage",
            ),
            self.PatientIncomingMessageTypes.ACTION_ADD: (self.handle_action_add,),
        }

    def connect(self):
        # example trainer creation for testing purposes as long as the actual exercise flow is not useful for patient route debugging
        self.tempExercise = Exercise.createExercise()
        # example patient creation for testing purposes as long as the actual patient flow is not implemented
        from template.tests.factories.patient_state_factory import PatientStateFactory

        self.temp_state = PatientStateFactory(10, 2)
        PatientInstance.objects.create(
            name="Max Mustermann",
            exercise=self.exercise,
            patient_id=2,  # has to be the same as the username in views.py#post
            exercise_id=self.tempExercise.id,
            patient_state=self.temp_state,
        )

        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get("token", [None])[0]
        success, patient_id = self.authenticate(token)
        if success:
            self.patient_instance = PatientInstance.objects.get(patient_id=patient_id)
            self.patient_id = patient_id
            self.exercise = self.patient_instance.exercise
            self.accept()
            self.subscribe(ChannelNotifier.get_group_name(self.patient_instance))
            self.subscribe(ChannelNotifier.get_group_name(self.exercise))
            self._send_exercise(exercise=self.exercise)
            self.send_available_actions()

    def disconnect(self, code):
        # example patient_instance deletion - see #connect
        self.patient_instance.delete()
        # example trainer deletion - see #connect
        self.tempExercise.delete()
        self.temp_state.delete()
        super().disconnect(code)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    # API Methods, open to client.
    # ------------------------------------------------------------------------------------------------------------------------------------------------
    def handle_example(self, exercise_code, patient_code):
        self.exercise_code = exercise_code
        self.patient_id = patient_code
        self.send_event(
            self.PatientOutgoingMessageTypes.RESPONSE,
            content=f"exercise_code {self.exercise_code} & patient_code {self.patient_id}",
        )

    def handle_test_passthrough(self):
        self.send_event(
            self.PatientOutgoingMessageTypes.TEST_PASSTHROUGH,
            message="received test event",
        )

    def handle_triage(self, triage):
        self.patient_instance.triage = triage
        self.patient_instance.save(update_fields=["triage"])
        self._send_exercise(exercise=self.exercise)

    def handle_action_add(self):
        self.patient_instance.add_action(self.tempExercise.action_set.first())
        self._send_exercise(exercise=self.exercise)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    # Events triggered internally by channel notifications
    # ------------------------------------------------------------------------------------------------------------------------------------------------

    def state_change_event(self, event):
        serialized_state = StateSerializer(self.patient_instance.state).data
        self.send_event(
            self.PatientOutgoingMessageTypes.STATE_CHANGE,
            **serialized_state,
        )

    def action_confirmation_event(self, event):
        action = ActionInstanceStateNames.objects.get(pk=event["action_pk"])
        self.send_event(
            self.PatientOutgoingMessageTypes.ACTION_CONFIRMATION,
            {"actionId": action.id, "actionName": action.name},
        )

    def action_declination_event(self, event):
        action = ActionInstanceStateNames.objects.get(pk=event["action_pk"])
        self.send_event(
            self.PatientOutgoingMessageTypes.ACTION_DECLINATION,
            {
                "actionName": action.name,
                "actionDeclinationReason": action.state.info_text,
            },
        )

    def action_result_event(self, event):
        action = ActionInstanceStateNames.objects.get(pk=event["action_pk"])
        self.send_event(
            self.PatientOutgoingMessageTypes.ACTION_RESULT,
            {
                "actionId": action.id,
                "actionResult": event["action_result"],
            },
        )
