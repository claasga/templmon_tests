import os
import re
import asyncio
import threading
import subprocess

# import log_transformer as lt
from . import signature_mapping as sm


class LogRule:
    # There may be only one LogRule instance with the same values for each exercise
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SUB_DIR = "log_rules"  # ToDo
    RULE_FILENAME = "mfotl"
    DEFAULT_SIGNATURE = os.path.join(BASE_DIR, "kdps.sig")

    def __init__(self, signature, templatefile):
        self.signature = signature
        self.templatefile = templatefile
        self.log_transformer = "jibbersih"  # lt.LogTransformer

    # def __del__(self):
    #    os.remove(self.templatefile)

    @classmethod
    def create(cls, rule: str, name: str):
        file_path = cls._generate_file_path(name)
        with open(file_path, "w") as f:
            f.write(rule)
        return cls(cls.DEFAULT_SIGNATURE, file_path)

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
        cls.create(rule, "personnel_prioritization")
        print(rule)


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
    def generate(cls, operator=">=", personnel_count=4):
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

        return cls.create(rule, "personnel_check")


class SymptomCombinationRule(LogRule):
    @classmethod
    def generate(
        cls,
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

        examination_formulas, examination_results_base_subs, c_examination_formulas = (
            None,
            None,
            None,
        )
        if examination_results:
            examination_formulas = sm.ExaminationResult.bulk_create(
                len(examination_results)
            )
            examination_formulas[0].match(examination_formulas[1:], [RP.PATIENT.name])
            for i, key in enumerate(examination_results.keys()):
                examination_formulas[i].set_variable(RP.EXAMINATION.name, f'"{key}"')
            examination_results_base_subs = [
                f"{examination_formulas[i].mfotl()} AND {examination_formulas[i].compare_values_mfotl(dict(list(examination_results.items())[i]))}"
                for i in range(len(examination_results))
            ]
            c_examination_formulas = sm.ExaminationResult.bulk_create(
                len(examination_results)
            )
            c_examination_formulas[0].match(
                c_examination_formulas[1:], [RP.PATIENT.name]
            )
            for i in range(len(examination_formulas)):
                c_examination_formulas[i].set_variable(
                    RP.EXAMINATION.name,
                    examination_formulas[i].get_variable(RP.EXAMINATION.name),
                )

        action_started, action_started_2, c_action_started, c_action_started_2 = (
            sm.ActionStarted.bulk_create(3)
        )
        action_started.match(
            [action_started_2, c_action_started, c_action_started_2], [RP.PATIENT.name]
        )
        action_started.set_variable(RP.ACTION.name, f'"{action}"')

        action_canceled = sm.ActionCanceled()
        action_started.match([action_canceled], [RP.PATIENT.name, RP.ACTION.name])
        recent_conditions = []
        examination_results_subs = []
        if examination_results:
            examination_results_subs = [
                f"""(NOT (EXISTS {examination_formulas[i].bind([RP.PATIENT], False)}. {examination_formulas[i].mfotl()})
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
            NOW_SINCE_CONSTRUCTS.append(
                " AND ".join(
                    NOW_versions[i] + SINCE_versions[:i] + SINCE_versions[i + 1 :]
                )
            )

        to_late_rule = f""" 
    (EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. ONCE[0,*] {patient_arrived.mfotl()})
AND    
            (NOT ({action_started.mfotl()}
        OR
            (EXISTS new_results. patient_examination_result(patient_id, "selected_examination_id", new_results))
        OR
            (EXISTS {c_changed_state.bind([RP.PATIENT.name], False)}. {c_changed_state.mfotl()}))
    SINCE[{timeframe},*] #hier andere struktur nötig, da diesmal die zeit relevant und nicht mit "*" als Obergrenze geschummelt werden kann
                        ({" OR ".join(NOW_SINCE_CONSTRUCTS)})"""
        wrong_order_rule = f"""
    ((EXISTS {patient_arrived.bind([RP.PATIENT.name], False)}. ONCE[0,*] {patient_arrived.mfotl()})
AND
        {action_started_2.mfotl()}
    AND
        NOT {action_started_2.compare_values_mfotl({RP.ACTION.name: f'"{action}"'})})
AND
    PREV
                (((NOT ((EXISTS new_results. patient_examination_result(patient_id, "selected_examination_id", new_results))
            OR
                (EXISTS {c_action_started.bind([RP.PATIENT.name], False)}. {c_action_started.mfotl()})))
        SINCE[0,*]
                patient_examination_result(patient_id, "selected_examination_id", results)
            AND
                results = "bad")
    AND
                (NOT ((EXISTS {c_changed_state.bind([RP.PATIENT.name], False)}. {c_changed_state.mfotl()})
            AND 
                (EXISTS {c_action_started_2.bind([RP.PATIENT.name], False)}. {c_action_started_2.mfotl()}))
        SINCE[0,*]
                {vital_parameters_sub}))"""

        pass


class LogRuleRunner:
    # I need to start monpoly before subscribing to the log or store the log entries
    loop = asyncio.new_event_loop()
    instances = []

    def __init__(
        self,
        exercise,
        log,
        log_rule: LogRule,
    ):
        self.log = log
        self.exercise = exercise
        self.log_rule = log_rule
        self.log_transformer = log_rule.log_transformer
        self.monpoly_started_event = asyncio.Event()
        self.finished_reading_monpoly = asyncio.Event()
        LogRuleRunner.instances.append(
            self
        )  # ToDo: remove when log rules get created inside trainer consumer

    def __del__(self):
        pass

    def receive_log_entry(self, log_entry):
        transformed_log_entry = self.log_transformer.transform(log_entry)
        asyncio.run_coroutine_threadsafe(
            self._write_log_entry(transformed_log_entry), self.loop
        )

    async def _write_log_entry(self, monpolified_log_entry: str):
        print(f"Received log entry: {monpolified_log_entry}")
        await self.monpoly_started_event.wait()  # Wait until monpoly is ready
        if self.monpoly.stdin:
            try:
                encoded = monpolified_log_entry.encode()
                self.monpoly.stdin.write(encoded)
                await self.monpoly.stdin.drain()
            except Exception as e:
                raise e
        else:
            raise Exception("Monpoly is not running")

    async def read_output(self, process, free_variables):
        def get_fullfilling_assignments(assignments_str: str):
            assignments = []
            i = 0
            print("Start mapping assignments")
            while i < len(assignments_str):
                if assignments_str[i] == "(":
                    j = i + 1
                    is_inside_quotes = False
                    while assignments_str[j] != ")" or is_inside_quotes:
                        j += 1
                    assignments.append(assignments_str[i + 1 : j])
                    i = j
                i += 1
            print("Finished mapping assignments with " + str(assignments))
            assignment_dict = {}
            for assignment in assignments:
                print(assignment)

                i = 0
                for free_variable in free_variables:
                    if i >= len(assignment):
                        raise Exception(
                            "Assignment does not contain all free variables"
                        )
                    inside_string = False
                    beginning_i = i
                    while i < len(assignment) and (
                        assignment[i] != "," or inside_string
                    ):
                        if assignment[i] == '"':
                            inside_string = not inside_string
                        i += 1
                    assignment_dict[free_variable] = assignment[beginning_i:i]
                    print(
                        f"Free variable: {free_variable}, Value: {assignment_dict[free_variable]}"
                    )
                if i < len(assignment):
                    raise Exception("Assignment contains more than the free variables")
                print(assignment_dict)
            return assignment_dict

        while True:
            line = await process.stdout.readline()
            if not line:
                print("process terminated")
                self.finished_reading_monpoly.set()
                break
            decoded_line = line.decode("utf-8")
            if decoded_line[0] != "@" or decoded_line[-3:-1] == "()":
                continue
            print("Received output:")
            print(decoded_line)
            decoded_line = decoded_line[1:]
            parts = decoded_line.split(" (")
            if len(parts) != 3:
                raise Exception("Invalid output format")

            timestamp = float(parts[0])
            timepoint = int(re.search(r"\d+", parts[1]).group())
            fullfilling_assignments = get_fullfilling_assignments(parts[2])
            for fullfilling_assignment in fullfilling_assignments:
                print(
                    f"Processed output : {timestamp}, {timepoint}, {fullfilling_assignment}"
                )

    async def _launch_monpoly(self, mfotl_path, sig_path, rewrite, free_variables):
        """Has to be launched in a separate thread"""
        self.monpoly = await asyncio.create_subprocess_exec(
            "monpoly",
            "-sig",
            sig_path,
            "-formula",
            mfotl_path,
            "-verbose",
            "" if rewrite else "-no_rw",
            env=os.environ.copy(),  # Ensure the environment variables are passed
            stdin=asyncio.subprocess.PIPE,  # Allow writing to stdin
            stdout=asyncio.subprocess.PIPE,  # Capture stdout
            stderr=asyncio.subprocess.PIPE,  # Optionally capture stderr
        )
        asyncio.create_task(self.read_output(self.monpoly, free_variables))
        self.monpoly_started_event.set()  # Signal that monpoly is ready

    async def terminate_monpoly(self):
        self.monpoly.stdin.close()
        await self.finished_reading_monpoly.wait()
        self.monpoly.terminate()

    def _extract_environment_variables(self, output: str):
        free_variables_predecessor = "The sequence of free variables is: ("
        start = output.find(free_variables_predecessor) + len(
            free_variables_predecessor
        )
        end = output.find(")", start)
        free_variables = output[start:end]
        free_variables = free_variables.split(",")
        print("Extracted environment variables:")
        for free_variable in free_variables:
            print(free_variable)
        return free_variables

    def _environment_infos(self):
        success_message = "formula is monitorable."
        output = subprocess.run(
            [
                "monpoly",
                "-sig",
                self.log_rule.signature,
                "-formula",
                self.log_rule.templatefile,
                "-check",
            ],
            capture_output=True,
            text=True,
        )
        if success_message in output.stdout:

            return True, self._extract_environment_variables(output.stdout)
        output = subprocess.run(
            [
                "monpoly",
                "-sig",
                self.log_rule.signature,
                "-formula",
                self.log_rule.templatefile,
                "-no_rw",
                "-check",
            ],
            capture_output=True,
            text=True,
        )
        if success_message in output.stdout:
            return False, self._extract_environment_variables(output.stdout)

        raise Exception(output.stderr)

    def start_log_rule(self):
        def launch_listener_loop(loop: asyncio.AbstractEventLoop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        if (not self.loop) or (not self.loop.is_running()):
            threading.Thread(target=launch_listener_loop, args=(self.loop,)).start()
        rewrite_allowed, self.free_variables = self._environment_infos()
        asyncio.run_coroutine_threadsafe(
            self._launch_monpoly(
                self.log_rule.templatefile,
                self.log_rule.signature,
                rewrite_allowed,
                self.free_variables,
            ),
            self.loop,
        )
        self.log.subscribe_to_exercise(self.exercise, self, send_past_logs=True)
        print(
            "self.log.subscribe_to_exercise(self.exercise, self, send_past_logs=True)"
        )

    def stop_log_rule(self):
        asyncio.run_coroutine_threadsafe(self.terminate_monpoly(), self.loop)


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
if __name__ == "main":
    RP = sm.RuleProperty
    PersonnelCheckRule.generate(operator="<")
    PersonnelPrioritizationRule.generate(
        RP.AIRWAY.name, ">", 4, 2, RP.CIRCULATION.name, "<", 4, 2
    )
