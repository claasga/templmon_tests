import os

if __name__ != "__main__":
    from . import signature_mapping as sm
    from . import log_transformer as lt
else:
    import signature_mapping as sm
    import log_transformer as lt


class ViolationType:
    DURATIONAL = 0
    SINGULAR = 1


class LogRule:
    # There may be only one LogRule instance with the same values for each exercise
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SUB_DIR = "log_rules"  # ToDo
    RULE_FILENAME = "mfotl"
    DEFAULT_SIGNATURE = os.path.join(BASE_DIR, "kdps.sig")

    def __init__(self, signature, rule_file_path, violation_type: ViolationType, name):
        self.signature = signature
        self.rule_file_path = rule_file_path
        self.log_transformer = lt.LogTransformer
        self.violation_type = violation_type
        self.name = name

    # def __del__(self):
    #    os.remove(self.rule_file_path)

    @classmethod
    def create(cls, rule: str, name: str, violation_type: ViolationType):
        file_path = cls._generate_file_path(name)
        with open(file_path, "w") as f:
            f.write(rule)
        return cls(cls.DEFAULT_SIGNATURE, file_path, violation_type, name)

    @classmethod
    def generate(cls):
        raise NotImplementedError

    @classmethod
    def _generate_file_path(cls, name):
        temp_path = os.path.join(
            cls.BASE_DIR, cls.SUB_DIR, f"{name}.{cls.RULE_FILENAME}"
        )
        i = 1
        while os.path.exists(temp_path):
            temp_path = os.path.join(
                cls.BASE_DIR, cls.SUB_DIR, f"{name}_{i}.{cls.RULE_FILENAME}"
            )
            i += 1
        return temp_path


class PersonnelPrioritizationRule(LogRule):
    @classmethod
    def generate(
        cls,
        name,
        vital_sign_p1,
        operator_p1,
        value_p1,
        personnel_count_p1,
        vital_sign_p2,
        operator_p2,
        value_p2,
        personnel_count_p2,
    ):
        RP = sm.RuleProperty
        patient_relocated_1, c_patient_relocated_1 = sm.PatientRelocated.bulk_create(2)
        patient_1_name = "pat_n_1"
        patient_relocated_1.set_variable(RP.PATIENT.name, patient_1_name)
        patient_arrived_1, patient_arrived_2 = sm.PatientArrived.bulk_create(2)
        changed_state_1, c_changed_state_1 = sm.ChangedState.bulk_create(2)
        selected_parameter_1 = "selected_parameter_1"
        changed_state_1.set_variable(vital_sign_p1, selected_parameter_1)
        changed_state_1.match([c_changed_state_1], [vital_sign_p1])
        assigned_personnel_1, assigned_personnel_2a, assigned_personnel_2b = (
            sm.AssignedPersonnel.bulk_create(3)
        )
        unassigned_personnel_1, unassigned_personnel_2a, unassigned_personnel_2b = (
            sm.UnassignedPersonnel.bulk_create(3)
        )
        assigned_personnel_1.match([unassigned_personnel_1], [RP.PERSONNEL.name])
        assigned_personnel_2a.match(
            [unassigned_personnel_2a, unassigned_personnel_2b, assigned_personnel_2b],
            [RP.PERSONNEL.name],
        )
        patient_relocated_1.match(
            [
                patient_arrived_1,
                c_patient_relocated_1,
                changed_state_1,
                c_changed_state_1,
                assigned_personnel_1,
            ],
            [RP.PATIENT.name],
        )
        patient_arrived_1.set_variable(
            RP.LOCATION.name, patient_relocated_1.get_variable(RP.NEW_LOCATION.name)
        )
        patient_relocated_2, c_patient_relocated_2 = sm.PatientRelocated.bulk_create(
            2, start_id=3
        )
        patient_2_name = "pat_n_2"
        patient_relocated_2.set_variable(RP.PATIENT.name, patient_2_name)
        changed_state_2, c_changed_state_2 = sm.ChangedState.bulk_create(2, start_id=3)
        selected_parameter_2 = "selected_parameter_2"
        changed_state_2.set_variable(vital_sign_p2, selected_parameter_2)
        changed_state_2.match([c_changed_state_2], [vital_sign_p2])
        patient_relocated_2.match(
            [
                patient_arrived_2,
                c_patient_relocated_2,
                assigned_personnel_2a,
                assigned_personnel_2b,
                c_changed_state_2,
                changed_state_2,
            ],
            [RP.PATIENT.name],
        )
        patient_arrived_2.set_variable(
            RP.LOCATION.name, patient_relocated_2.get_variable(RP.NEW_LOCATION.name)
        )

        rule = f"""
EXISTS {changed_state_1.bind([RP.PATIENT.name, vital_sign_p1], False)}, {changed_state_2.bind([RP.PATIENT.name, vital_sign_p2, RP.DEAD.name], False)}.
                (((NOT (EXISTS {c_patient_relocated_1.bind([RP.PATIENT.name], False)}. {c_patient_relocated_1.mfotl()}))
            SINCE[0,*]
                (EXISTS {patient_relocated_1.bind([RP.OLD_LOCATION.name])}. ({patient_relocated_1.mfotl()})))
        OR
                ((EXISTS {patient_arrived_1.bind([RP.PATIENT.name, RP.LOCATION.name], False)}. ONCE[0,*] {patient_arrived_1.mfotl()})
            AND
                (NOT (EXISTS {c_patient_relocated_1.bind([RP.PATIENT.name], False)}. ONCE[0,*] {c_patient_relocated_1.mfotl()}))))
    AND
                (((NOT (EXISTS {c_patient_relocated_2.bind([RP.PATIENT.name], False)}. {c_patient_relocated_2.mfotl()}))
            SINCE[0,*]
                    (EXISTS {patient_relocated_2.bind([RP.PATIENT.name, RP.NEW_LOCATION.name], include=False)}. ({patient_relocated_2.mfotl()})))
        OR
                ((EXISTS {patient_arrived_2.bind([RP.PATIENT.name, RP.LOCATION.name], False)}. ONCE[0,*] {patient_arrived_2.mfotl()})
            AND
                (NOT (EXISTS {c_patient_relocated_2.bind([RP.PATIENT.name], False)}. ONCE[0,*] {c_patient_relocated_2.mfotl()}))))
    AND
        NOT {patient_relocated_1.get_variable(RP.PATIENT.name)} = {patient_relocated_2.get_variable(RP.PATIENT.name)}
    AND
        {patient_relocated_1.get_variable(RP.NEW_LOCATION.name)} = {patient_relocated_2.get_variable(RP.NEW_LOCATION.name)}
AND 
            ((NOT EXISTS {c_changed_state_1.bind([RP.PATIENT.name], False)}. {c_changed_state_1.mfotl()})
        SINCE[0,*]
            {changed_state_1.mfotl()})
    AND
        4.0 < {selected_parameter_1} 
    AND
        {selected_parameter_1} < 8.0
AND
            ((NOT EXISTS {c_changed_state_2.bind([RP.PATIENT.name], False)}. {c_changed_state_2.mfotl()})
        SINCE[0,*]
            {changed_state_2.mfotl()})
    AND
        4.0 >= {selected_parameter_2}
    AND
        {selected_parameter_2} >= 0.0
    AND
        {changed_state_2.get_variable(RP.DEAD.name)} = "FALSE"
AND
            (NOT
                (EXISTS {unassigned_personnel_2a.bind([RP.PERSONNEL.name])}.
                        (NOT {unassigned_personnel_2a.mfotl()} 
                    SINCE[0,*] 
                        {assigned_personnel_2a.mfotl()}))
        OR
            (EXISTS personnel_count.
                    (personnel_count <- CNT {assigned_personnel_2b.bind([RP.PERSONNEL.name])};{assigned_personnel_2b.bind([RP.PATIENT.name])}
                                (NOT {unassigned_personnel_2b.mfotl()}
                            ) SINCE[0,*] 
                                {assigned_personnel_2b.mfotl()})
                AND 
                    personnel_count < {personnel_count_p2}))
    AND
        (EXISTS personnel_count.
                (personnel_count <- CNT {assigned_personnel_1.bind([RP.PERSONNEL.name])};{assigned_personnel_1.bind([RP.PATIENT.name])}
                    (NOT {unassigned_personnel_1.mfotl()}) 
                    SINCE[0,*] 
                    {assigned_personnel_1.mfotl()})
            AND 
                personnel_count >= 2)
"""
        print(rule)
        return cls.create(
            rule, "personnel_prioritization", ViolationType.DURATIONAL, name
        )


class PersonnelCheckRule(LogRule):

    @classmethod
    def bigger_equal_then(
        cls, personnel_count, patient_arrived, unassigned_personnel, assigned_personnel
    ):
        RP = sm.RuleProperty
        rule = f"""
    (EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. 
        ONCE[0,*) {patient_arrived.mfotl()}) 
AND
        ((personnel_count <- CNT {RP.PERSONNEL};{RP.PATIENT} 
                (NOT {unassigned_personnel.mfotl()}) 
            SINCE[0,*)
                {assigned_personnel.mfotl()})
    AND 
        personnel_count >= {personnel_count})
"""
        print(rule)
        return rule

    @classmethod
    def smaller_then(
        cls,
        personnel_count,
        patient_arrived,
        unassigned_personnel,
        unassigned_personnel_2,
        assigned_personnel,
        assigned_personnel_2,
    ):
        RP = sm.RuleProperty
        rule = f"""
    ((EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. 
        ONCE[0,*) {patient_arrived.mfotl()}) 
    AND 
            (NOT EXISTS {unassigned_personnel_2.bind(include=False)}. 
                    ((NOT {unassigned_personnel_2.mfotl()}) 
                SINCE[0,*) {assigned_personnel_2.mfotl()}))) 
OR 
    ((EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. 
            ONCE[0,*) {patient_arrived.mfotl()}) 
        AND 
            (EXISTS personnel_count. 
                    ((personnel_count <- CNT {RP.PERSONNEL};{RP.PATIENT} 
                            ((NOT {unassigned_personnel.mfotl()}) 
                        SINCE[0,*) 
                            {assigned_personnel.mfotl()})) 
                AND 
                    personnel_count < {personnel_count})))
"""
        return rule

    @classmethod
    def generate(cls, name, operator=">=", personnel_count=4):
        if operator not in [">=", "<", "="]:
            raise ValueError("Invalid operator")
        if operator == ">=" and personnel_count == 0:
            raise ValueError(
                "Pointless monitoring. All patient instances have a personnel count of 0. Please increase"
            )
        RP = sm.RuleProperty
        assigned_personnel = sm.AssignedPersonnel()
        unassigned_personnel = sm.UnassignedPersonnel()
        patient_arrived = sm.PatientArrived()
        rule = None
        if operator == ">=":
            rule = cls.bigger_equal_then(
                personnel_count,
                patient_arrived,
                unassigned_personnel,
                assigned_personnel,
            )
        else:
            assigned_personnel_2 = sm.AssignedPersonnel()
            personnel_name = RP.PERSONNEL.name + "2"
            assigned_personnel_2.set_variable(RP.PERSONNEL.name, personnel_name)
            unassigned_personnel_2 = sm.UnassignedPersonnel()
            unassigned_personnel_2.set_variable(RP.PERSONNEL.name, personnel_name)
            rule = cls.smaller_then(
                personnel_count,
                patient_arrived,
                unassigned_personnel,
                unassigned_personnel_2,
                assigned_personnel,
                assigned_personnel_2,
            )

        return cls.create(rule, "personnel_check", ViolationType.DURATIONAL, name)


class SymptomCombinationRule(LogRule):
    @classmethod
    def generate(
        cls,
        name,
        action,
        timeframe,
        vital_parameters: dict = None,
        examination_results: dict = None,
    ):
        if not vital_parameters and not examination_results:
            raise ValueError("No parameters to monitor")

        RP = sm.RuleProperty
        patient_arrived = sm.PatientArrived()
        changed_state, c_changed_state, vital_parameters_sub = None, None, None

        if vital_parameters:
            [changed_state, c_changed_state] = sm.ChangedState.bulk_create(2)
            vital_parameters_sub = f"""{changed_state.mfotl()} AND {changed_state.compare_values_mfotl(vital_parameters)}"""
            patient_arrived.match([changed_state, c_changed_state], [RP.PATIENT.name])

        examination_formulas, examination_results_base_subs, c_examination_formulas = (
            None,
            None,
            None,
        )
        if examination_results:
            examination_formulas = sm.ExaminationResult.bulk_create(
                len(examination_results)
            )
            patient_arrived.match(examination_formulas, [RP.PATIENT.name])
            for i, key in enumerate(examination_results.keys()):
                examination_formulas[i].set_variable(RP.EXAMINATION.name, f'"{key}"')
            examination_results_base_subs = [
                f"{form.mfotl()}{(' AND ' + cmp) if (cmp := form.compare_values_mfotl({RP.EXAMINATION.name: value})) else ''}"
                for form, (key, value) in zip(
                    examination_formulas, examination_results.items()
                )
            ]
            c_examination_formulas = sm.ExaminationResult.bulk_create(
                len(examination_results), start_id=len(examination_results) + 1
            )
            patient_arrived.match(c_examination_formulas, [RP.PATIENT.name])
            for i in range(len(examination_formulas)):
                c_examination_formulas[i].set_variable(
                    RP.EXAMINATION.name,
                    examination_formulas[i].get_variable(RP.EXAMINATION.name),
                )

        action_started, action_started_2, c_action_started, c_action_started_2 = (
            sm.ActionStarted.bulk_create(4)
        )
        patient_arrived.match(
            [action_started, action_started_2, c_action_started, c_action_started_2],
            [RP.PATIENT.name],
        )
        action_started.set_variable(RP.ACTION.name, f'"{action}"')

        action_canceled = sm.ActionCanceled()
        action_started.match([action_canceled], [RP.PATIENT.name, RP.ACTION.name])
        recent_conditions = []
        examination_results_subs = []
        if examination_results:
            examination_results_subs = [
                f"""(NOT (EXISTS {c_examination_formulas[i].bind([RP.PATIENT.name], False)}. {c_examination_formulas[i].mfotl()})
            SINCE[0,*]
                   {subs})"""
                for i, subs in enumerate(examination_results_base_subs)
            ]
            recent_conditions.append(f"{' AND '.join(examination_results_subs)}")
        if vital_parameters:
            vital_parameters_sub = f"""(NOT EXISTS {c_changed_state.bind([RP.PATIENT.name], False)}. {c_changed_state.mfotl()}
            SINCE[0,*] 
                {changed_state.mfotl()} AND {changed_state.compare_values_mfotl(vital_parameters)})"""
            recent_conditions.append(vital_parameters_sub)
        unfinished_rule = f"""
        (EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. ONCE[0,*] {patient_arrived.mfotl()})
AND
    {action_canceled.mfotl()}
AND
        (NOT {action_started.mfotl()}
    SINCE[0,{timeframe}] # hier dauer der Aktion eintragen!
            ({action_started.mfotl()} #Currently uses examination and breathing values of the action started timpoint. Might be unintented behaviour. Or not.
        AND
            {" AND ".join(recent_conditions)}))
# struggles with overlapping actions of the same type. When canceled, it always asumes the most"""

        NOW_versions = examination_results_base_subs + [
            f"{changed_state.mfotl()} AND {changed_state.compare_values_mfotl(vital_parameters)}"
        ]
        SINCE_versions = examination_results_subs + [vital_parameters_sub]
        NOW_SINCE_CONSTRUCTS = []
        for i in range(len(NOW_versions)):
            conditions = (
                [NOW_versions[i]] + SINCE_versions[:i] + SINCE_versions[i + 1 :]
            )
            NOW_SINCE_CONSTRUCTS.append(" AND ".join(conditions))
        CONDITIONS_CONSTRUCTS = [
            action_started.mfotl(),
            f"(EXISTS {c_changed_state.bind([RP.PATIENT.name], False)}. {c_changed_state.mfotl()})",
        ]
        for form in c_examination_formulas:
            CONDITIONS_CONSTRUCTS.append(
                f"EXISTS {form.bind([RP.PATIENT.name, RP.EXAMINATION.name], False)}. {form.mfotl()}"
            )
        to_late_rule = f""" 
    (EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. ONCE[0,*] {patient_arrived.mfotl()})
AND    
            (NOT ({" OR ".join(f"({cc})" for cc in CONDITIONS_CONSTRUCTS)}))
    SINCE[{timeframe},*] #hier andere struktur nötig, da diesmal die zeit relevant und nicht mit "*" als Obergrenze geschummelt werden kann
                        ({" OR ".join([f"({nsc})" for nsc in NOW_SINCE_CONSTRUCTS])})"""

        RECENT_EXAMINATIONS_CONSTRUCT = [
            f"""((NOT ((EXISTS {c_form.bind([RP.PATIENT.name], False)}. {c_form.mfotl()})
            OR
                (EXISTS {c_action_started.bind([RP.PATIENT.name], False)}. {c_action_started.mfotl()})))
        SINCE[0,*]
                {form.mfotl()}{' AND ' + cmp if (cmp:=form.compare_values_mfotl({RP.RESULT.name: value})) else ''})"""
            for form, c_form, value in list(
                zip(
                    examination_formulas,
                    c_examination_formulas,
                    examination_results.values(),
                )
            )
        ]
        RECENT_STATES_CONSTRUCT = f"""(NOT ((EXISTS {c_changed_state.bind([RP.PATIENT.name], False)}. {c_changed_state.mfotl()})
            AND 
                (EXISTS {c_action_started_2.bind([RP.PATIENT.name], False)}. {c_action_started_2.mfotl()}))
        SINCE[0,*]
                ({changed_state.mfotl()} AND {changed_state.compare_values_mfotl(vital_parameters)}))"""
        wrong_order_rule = f"""
    ((EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. ONCE[0,*] {patient_arrived.mfotl()})
AND
        {action_started_2.mfotl()}
    AND
        NOT {action_started_2.compare_values_mfotl({RP.ACTION.name: action})})
AND
    PREV
                ({" AND ".join(RECENT_EXAMINATIONS_CONSTRUCT + [RECENT_STATES_CONSTRUCT])})"""

        return [
            cls.create(
                wrong_order_rule,
                "wrong_order",
                ViolationType.SINGULAR,
                f"{name}_wrong_order",
            ),
            cls.create(
                to_late_rule, "to_late", ViolationType.DURATIONAL, f"{name}_to_late"
            ),
            cls.create(
                unfinished_rule,
                "unfinished",
                ViolationType.SINGULAR,
                f"{name}_unfinished",
            ),
        ]


# from ..channel_notifications import LogEntryDispatcher
#
# test_rule_str = """    (personnel_count <- CNT personnel_id;patient_id
#            (NOT unassigned_personnel(personnel_id))
#        SINCE[0,*]
#            assigned_personnel(personnel_id, patient_id))
# AND
#    (personnel_count >= 4)"""
# test_rule = LogRule.create(test_rule_str, "test_rule")
# log_rule_runner = LogRuleRunner(None, LogEntryDispatcher, test_rule)
if __name__ == "__main__":
    RP = sm.RuleProperty
    # PersonnelCheckRule.generate(operator="<")
    # PersonnelPrioritizationRule.generate(
    #    RP.AIRWAY.name, ">", 4, 2, RP.CIRCULATION.name, "<", 4, 2
    # )
    SymptomCombinationRule.generate(
        "selected_action_id",
        120,
        {RP.CIRCULATION.name: 10.0},
        {"selected_examination_id": "bad"},
    )
# String vs int bei 0 in monpoly
# To Late:
# 1. ~~patienten_id wird gebunden in unterem part~~
# 2. ~~string gebundene variablen werden nochmals gebunden~~
# 3. ~~klammerung ums or fehlt~~
# 4. ~~c_version wird nicht verwendet~~
# 5. Examination results werden nicht getestet
