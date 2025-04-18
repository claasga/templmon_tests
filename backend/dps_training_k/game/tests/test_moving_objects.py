from django.test import TestCase

from template.tests.factories import ActionFactory, ConditionFactory
from .factories import (
    AreaFactory,
    PatientFactory,
    ActionInstanceFactory,
    PersonnelFactory,
)
from .mixin import TestUtilsMixin
from ..models import ActionInstanceStateNames


class PatientMovingTestCase(TestCase, TestUtilsMixin):
    def setUp(self):
        self.area = AreaFactory()
        self.area2 = AreaFactory(name="Area2")
        self.patient = PatientFactory()
        self.personnel = PersonnelFactory(patient_instance=self.patient)

    def test_moving_patient_with_assigned_resources(self):
        """
        When a patient is moved, all assigned resources are automatically released and the patient has a new area and has no assigned
        personnel or material anymore as the resources are automatically unassigned and a warning is given.
        However, if an action is scheduled, the resources are blocked and cannot be released. Consequently, the patient cannot be moved,
        keeping its original area.
        """

        self.assertEqual(self.patient.personnel_assigned(), [self.personnel])
        self.assertEqual(self.patient.personnel_available(), [self.personnel])

        action_instance = ActionInstanceFactory(
            patient_instance=self.patient,
            template=ActionFactory(conditions=ConditionFactory(num_personnel=1)),
        )
        self.personnel.block(action_instance)

        self.assertEqual(
            self.personnel.try_moving_to(self.area),
            (False, "Maxim Musterfrau ist blockiert und kann nicht verlegt werden."),
        )
        self.personnel.release()
        action_instance._update_state(ActionInstanceStateNames.FINISHED)

        self.assertEqual(
            self.patient.try_moving_to(self.area2),
            (True, "Warnung: Ressourcen wurden automatisch freigegeben"),
        )

        self.assertEqual(self.patient.personnel_assigned(), [])
        self.assertEqual(self.patient.personnel_available(), [])
