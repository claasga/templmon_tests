from django.test import TestCase
from ..channel_notifications import LogEntryDispatcher
from ..templmon import LogRule, RuleRunner, LogTransformer
from .factories import LogEntryFactoryPersonnelAssigned
from .factories import PersonnelFactory, PatientFactory, ExerciseFactory
from .mixin import TestUtilsMixin
from unittest.mock import patch


class LogRuleTestCase(TestUtilsMixin, TestCase):
    @patch("game.templmon.rule_runner.RuleRunner.receive_log_entry")
    def test_creation(self, received_log):
        test_rule_str = """    (personnel_count <- CNT personnel_id;patient_id 
            (NOT unassigned_personnel(personnel_id)) 
        SINCE[0,*] 
            assigned_personnel(personnel_id, patient_id))
AND
    (personnel_count >= 4)"""
        used_dispatchers = [
            "LogEntryDispatcher",
            "PersonnelDispatcher",
            "PatientInstanceDispatcher",
        ]
        for dispatcher in used_dispatchers:
            self.deactivate_dispatching(dispatcher)

        test_rule = LogRule.create(test_rule_str, "test_rule")
        exercise = ExerciseFactory()
        log_rule_runner = RuleRunner(exercise, LogEntryDispatcher, test_rule)

        patient = PatientFactory()
        exercise = patient.exercise
        exercise.update_state(exercise.StateTypes.RUNNING)
        # self.assertTrue(personnel.try_moving_to(patient)[0])

        personnel = PersonnelFactory(patient_instance=patient)
        log_rule_runner.start()
        log_entry = LogEntryFactoryPersonnelAssigned(
            patient_instance=patient, personnel=[personnel]
        )
        # log_entry.save()
        self.assertGreater(received_log.call_count, 0)
