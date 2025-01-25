import os
import re
import asyncio
import threading
import subprocess

# from .log_transformer import LogTransformer


class LogRule:
    # There may be only one LogRule instance with the same values for each exercise
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SUB_DIR = "log_rules"  # ToDo
    RULE_FILENAME = "mfotl"
    DEFAULT_SIGNATURE = os.path.join(BASE_DIR, "kdps.sig")

    def __init__(self, signature, templatefile):
        self.signature = signature
        self.templatefile = templatefile
        self.log_transformer = LogTransformer

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
        pass


class PersonnelCheckRule(LogRule):
    @classmethod
    def generate(cls, operator=">=", personnel_count=4):
        if operator not in [">=", "<", "="]:
            raise ValueError("Invalid operator")
        if operator == ">=" and personnel_count == 0:
            raise ValueError(
                "Pointless monitoring. All patient instances have a personnel count of 0. Please increase"
            )
        import signature_mapping as sm

        assigned_personnel = sm.AssignedPersonnel()
        unassigned_personnel = sm.UnassignedPersonnel()
        patient_arrived = sm.PatientArrived()
        resulting_string = None
        if operator == ">=":
            resulting_string = f"""
    (EXISTS {patient_arrived.bind([sm.RuleProperty.PATIENT.name])}. 
        ONCE[0,*) {patient_arrived.mfotl()}) 
AND
        ((personnel_count <- CNT {sm.RuleProperty.PERSONNEL};{sm.RuleProperty.PATIENT} 
                (NOT {unassigned_personnel.mfotl()}) 
            SINCE[0,*)
                {assigned_personnel.mfotl()})
    AND 
        personnel_count >= {personnel_count})
"""
        else:
            assigned_personnel_2 = sm.AssignedPersonnel()
            personnel_name = sm.RuleProperty.PERSONNEL.name + "2"
            assigned_personnel_2.set_variable(
                sm.RuleProperty.PERSONNEL.name, personnel_name
            )
            unassigned_personnel_2 = sm.UnassignedPersonnel()
            unassigned_personnel_2.set_variable(
                sm.RuleProperty.PERSONNEL.name, personnel_name
            )
            resulting_string = f"""
    ((EXISTS {patient_arrived.bind([sm.RuleProperty.PATIENT.name])}. 
        ONCE[0,*) {patient_arrived.mfotl()}) 
    AND 
            (NOT EXISTS {unassigned_personnel_2.bind()}. 
                    ((NOT {unassigned_personnel_2.mfotl()}) 
                SINCE[0,*) {assigned_personnel_2.mfotl()}))) 
OR 
    ((EXISTS {patient_arrived.bind([sm.RuleProperty.PATIENT.name])}. 
            ONCE[0,*) {patient_arrived.mfotl()}) 
        AND 
            (EXISTS personnel_count. 
                    ((personnel_count <- CNT {sm.RuleProperty.PERSONNEL};{sm.RuleProperty.PATIENT} 
                            ((NOT {unassigned_personnel.mfotl()}) 
                        SINCE[0,*) 
                            {assigned_personnel.mfotl()})) 
                AND 
                    personnel_count {operator} {personnel_count})))
"""
        print(resulting_string)


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
PersonnelCheckRule.generate(operator="<")
