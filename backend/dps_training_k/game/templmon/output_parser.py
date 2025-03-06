import re
import asyncio

if __name__ != "__main__":
    from .log_transformer import MonpolyLogEntry


class ViolationTracker:
    def __init__(self, keys, violation_listener, session_id, rule_name, template_name):
        self._keys = keys
        self._violation_listener = violation_listener
        self._session_id = session_id
        self._rule_name = rule_name
        self._template_name = template_name

    async def update_violations(self, timestamp, timepoint, violations: list[dict]):
        pass

    def get_format(self):
        return self._keys


class SingularViolationTracker(ViolationTracker):
    async def update_violations(
        self,
        timestamp,
        timepoint,
        violations: list[dict],
        input_type,
        measurement_begin,
    ):
        for violation in violations:
            await self._violation_listener.dispatch_singular_violation(
                self._session_id,
                self._rule_name,
                self._template_name,
                dict(zip(self._keys, violation)),
                timestamp,
                timepoint,
                input_type,
            )
        await self._violation_listener.dispatch_processing_finished(
            self._session_id,
            self._rule_name,
            self._template_name,
            input_type,
            measurement_begin,
        )


class DurationalViolationTracker(ViolationTracker):
    def __init__(
        self,
        keys,
        same_violation_keys,
        violation_listener,
        session_id,
        rule_name,
        template_name,
    ):
        super().__init__(keys, violation_listener, session_id, rule_name, template_name)
        self.current_unfinished_violations = {}
        if not same_violation_keys:
            raise ValueError(
                "len(same_violation_keys)==0! Duration of errors for violations without defintion of violation instance cannot be calculated"
            )
        self.same_violation_keys = same_violation_keys

    async def _add_violations(
        self, timestamp, timepoint, filtered_violations, input_type
    ):
        for violation in filtered_violations:
            self.current_unfinished_violations[violation] = (timestamp, timepoint)
            await self._violation_listener.dispatch_durational_violation_started(
                self._session_id,
                self._rule_name,
                self._template_name,
                dict(zip(self.same_violation_keys, violation)),
                timestamp,
                timepoint,
                input_type,
            )

    async def _remove_violations(
        self, timestamp, timepoint, filtered_violations, input_type
    ):
        for violation in filtered_violations:
            start_stamp, start_point = self.current_unfinished_violations.pop(violation)
            await self._violation_listener.dispatch_durational_violation_finished(
                self._session_id,
                self._rule_name,
                self._template_name,
                dict(zip(self.same_violation_keys, violation)),
                start_stamp,
                start_point,
                timestamp,
                timepoint,
                input_type,
            )

    async def _change_violations(self, timestamp, timepoint, violations, input_type):
        for violation in violations:
            await self._violation_listener.dispatch_durational_violation_update(
                self._session_id,
                self._rule_name,
                self._template_name,
                dict(zip(self._keys, violation)),
                timestamp,
                timepoint,
                input_type,
            )

    async def update_violations(
        self,
        timestamp,
        timepoint,
        violations: list[dict],
        input_type,
        measurement_begin,
    ):
        """Assumes that violations are unique. For MonPoly they are"""
        unfinished_keys = list(self.current_unfinished_violations.keys())
        if len(violations) == 0:

            await self._remove_violations(
                timestamp, timepoint, unfinished_keys, input_type
            )
            await self._violation_listener.dispatch_processing_finished(
                self._session_id,
                self._rule_name,
                self._template_name,
                input_type,
                measurement_begin,
            )
            return

        violations_filtered = [
            tuple(
                [
                    value
                    for key, value in violation.items()
                    if key in self.same_violation_keys
                ]
            )
            for violation in violations
        ]
        violations_comparable = [tuple(violation.values()) for violation in violations]
        violations_filtered, violations_comparable = [
            list(group)
            for group in zip(*sorted(zip(violations_filtered, violations_comparable)))
        ]
        violations_to_add = []
        violations_to_remove = []
        violations_to_change = []

        while True:
            new_violation = violations_filtered.pop(0) if violations_filtered else None

            unfinished_violation = unfinished_keys.pop(0) if unfinished_keys else None
            if new_violation == None and unfinished_violation == None:
                break

            if new_violation == unfinished_violation:
                violations_to_change.append(violations_comparable.pop(0))
                continue
            elif new_violation and (
                not unfinished_violation or new_violation < unfinished_violation
            ):
                violations_to_add.append(new_violation)
                violations_to_change.append(violations_comparable.pop(0))
                unfinished_keys.insert(0, unfinished_violation)
            elif not new_violation or new_violation > unfinished_violation:
                violations_to_remove.append(unfinished_violation)
                violations_comparable.insert(0, new_violation)
        await self._add_violations(timestamp, timepoint, violations_to_add, input_type)
        await self._remove_violations(
            timestamp, timepoint, violations_to_remove, input_type
        )
        await self._change_violations(
            timestamp, timepoint, violations_to_change, input_type
        )
        await self._violation_listener.dispatch_processing_finished(
            self._session_id,
            self._rule_name,
            self._template_name,
            input_type,
            measurement_begin,
        )


class OutputParser:
    def __init__(
        self, process, output_receiver: ViolationTracker, pending_inputs_owner
    ):
        self.process = process
        self.output_receiver = output_receiver
        self.matches_seperator = " ("
        self.value_seperator = ","
        self.finished_reading_process = asyncio.Event()
        self.pending_inputs_owner = pending_inputs_owner
        self.commit_count = 0

    async def read_output(self):
        def get_fullfilling_assignments(assignments_str: str):
            assignments = []
            i = 0
            while i < len(assignments_str):
                if assignments_str[i] == "(":
                    j = i + 1
                    inside_string = False  # is Inside quotes wird nicht genutzt
                    while assignments_str[j] != ")" or inside_string:
                        if assignments_str[j] == '"':
                            inside_string = not inside_string
                        j += 1
                    if (asgnm := assignments_str[i + 1 : j]) and asgnm != "":
                        assignments.append(asgnm)
                    i = j
                i += 1
            if not assignments:
                return assignments
            assignment_dicts = []
            for assignment in assignments:

                i = 0
                assignment_dict = {}
                for free_variable in self.output_receiver.get_format():
                    if i >= len(assignment):
                        raise Exception(
                            "Assignment does not contain all free variables"
                        )
                    inside_string = False
                    beginning_i = i
                    while i < len(assignment) and (
                        assignment[
                            i : min(i + len(self.value_seperator), len(assignment))
                        ]
                        != self.value_seperator
                        or inside_string
                    ):
                        if assignment[i] == '"':
                            inside_string = not inside_string
                        i += 1
                    assignment_dict[free_variable] = assignment[beginning_i:i]
                    i += len(self.value_seperator)
                if i < len(assignment):
                    raise Exception("Assignment contains more than the free variables")
                assignment_dicts.append(assignment_dict)
            return assignment_dicts

        while True:
            print("OP: waiting for output")
            line = await self.process.stdout.readline()
            if not line:
                print("process terminated")
                self.finished_reading_process.set()
                break
            decoded_line = line.decode("utf-8")

            if decoded_line[0] != "@":
                if decoded_line[:2] != "At":
                    print(f"OP: WARNING: {decoded_line[:-1]}")
                continue

            self.pending_inputs_owner.output_read.set()
            print(f"OP: got {decoded_line[:-1]}")
            corresponding_input, measurement_begin = (
                await self.pending_inputs_owner.pending_inputs.get()
            )
            print(
                f"OP: Queue size is now {self.pending_inputs_owner.pending_inputs.qsize()}, consumed: {corresponding_input}"
            )
            if corresponding_input == MonpolyLogEntry.COMMIT:
                self.commit_count += 1
                continue
            # print(
            #    f"OUT: ({self.pending_inputs_owner.log_rule.template_name}, {self.pending_inputs_owner.log_rule.rule_name}): {decoded_line}"
            # )
            decoded_line = decoded_line[1:]
            parts = decoded_line.split(self.matches_seperator)
            if len(parts) != 3:
                raise Exception("Invalid output format")

            timestamp = float(parts[0])
            timepoint = int(re.search(r"\d+", parts[1]).group())
            timepoint -= self.commit_count
            fullfilling_assignments = get_fullfilling_assignments(parts[2])

            await self.output_receiver.update_violations(
                timestamp,
                timepoint,
                fullfilling_assignments,
                corresponding_input,
                measurement_begin,
            )


# async def main():
#    await get_output(
#        open(
#            "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/proto.txt",
#            "r",
#        ),
#        DurationalViolationReceiver(free_variables, ViolationDispatcher),
#    )
#    print("Finished")
#
#
# asyncio.run(main())
# get_output(
#    open(
#        "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/proto.txt",
#        "r",
#    ),
#    DurationalViolationReceiver(free_variables, ViolationDispatcher),
# )
if __name__ == "__main__":
    random = "ad"
    DurationalViolationTracker(
        ["pat_2", "pat_3"],
        random,
        "nzagkj",
    )
