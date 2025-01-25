import factory
from game.models import LogEntry
from .exercise_factory import ExerciseFactory
from .personnel_factory import PersonnelFactory
from .patient_factory import PatientFactory
from django.utils import timezone


class LogEntryFactoryPersonnelAssigned(factory.django.DjangoModelFactory):
    class Meta:
        model = LogEntry
        django_get_or_create = ["local_id"]

    local_id = 1
    exercise = factory.SubFactory(ExerciseFactory)
    timestamp = factory.LazyFunction(timezone.now)
    category = LogEntry.CATEGORIES.PERSONNEL
    type = LogEntry.TYPES.ASSIGNED
    is_dirty = True
    patient_instance = factory.SubFactory(PatientFactory)

    @factory.post_generation
    def personnel(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of personnel was passed in, use them
            self.personnel.set(extracted)
        else:
            # Assign a single Personnel instance
            self.personnel.set([PersonnelFactory()])
        self.set_dirty(False)
