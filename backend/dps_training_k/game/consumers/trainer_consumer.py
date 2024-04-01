from .abstract_consumer import AbstractConsumer
from game.models import Exercise


class TrainerConsumer(AbstractConsumer):
    """
    This class is responsible for DECODING messages from the frontend(user==trainer) into method calls and
    ENCODING events from the backend into JSONs to send to the frontend. When encoding events this also implies
    deciding what part of the event should be sent to the frontend(filtering).
    """

    class TrainerIncomingMessageTypes:
        EXAMPLE = "example"
        EXERCISE_CREATE = "trainer-exercise-create"
        TEST_PASSTHROUGH = "test-passthrough"
        EXERCISE_START = "exercise-start"
        EXERCISE_STOP = "exercise-stop"
        EXERCISE_PAUSE = "exercise-pause"
        EXERCISE_RESUME = "exercise-resume"

    class TrainerOutgoingMessageTypes:
        RESPONSE = "response"
        EXERCISE_CREATED = "trainer-exercise-create"
        TEST_PASSTHROUGH = "test-passthrough"
        EXERCISE_STARTED = "exercise-start"
        EXERCISE_STOPED = "exercise-stop"
        EXERCISE_PAUSED = "exercise-pause"
        EXERCISE_RESUMED = "exercise-resume"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exercise_code = None
        self.REQUESTS_MAP = {
            self.TrainerIncomingMessageTypes.EXAMPLE: (
                self.handle_example,
                "exercise_code",
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_CREATE: (
                self.handle_create_exercise,
            ),
            self.TrainerIncomingMessageTypes.TEST_PASSTHROUGH: (
                self.handle_test_passthrough,
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_START: (
                self.handle_start_exercise,
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_STOP: (
                self.handle_stop_exercise,
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_PAUSE: (
                self.handle_pause_exercise,
            ),
            self.TrainerIncomingMessageTypes.EXERCISE_RESUME: (
                self.handle_resume_exercise,
            ),
        }

    def connect(self):
        self.accept()

    def handle_example(self, exercise_code):
        self.exercise_code = exercise_code
        self.send_event(
            self.TrainerOutgoingMessageTypes.RESPONSE,
            content=f"exercise_code {self.exercise_code}",
        )

    def handle_create_exercise(self):
        self.exercise = Exercise.createExercise()
        self._send_exercise()

    def handle_test_passthrough(self):
        self.send_event(
            self.TrainerOutgoingMessageTypes.TEST_PASSTHROUGH,
            message="received test event",
        )

    def handle_start_exercise(self):
        # Start Celery
        # Start all objects with zero time tracks
        # Schedule phase transitions
        # Stop everything using NestedEventable
        pass

    def handle_stop_exercise(self):
        # Stop Celery
        # Stop all objects with all time tracks
        # Stop phase transitions
        # Stop laboratory
        # Stop measures
        # Stop everything using NestedEventable
        pass

    def handle_pause_exercise(self):
        pass

    def handle_resume_exercise(self):
        pass
