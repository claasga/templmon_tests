import re
import asyncio

free_variables = ["personnel_id", "patient_id"]


class ViolationDispatcher:
    @classmethod
    def dispatch_violation_started(cls, violation_assignment, start_stamp, start_point):
        print(f"Durational Violation started at {start_stamp}: {violation_assignment}")

    @classmethod
    def dispatch_violation_finished(
        cls,
        violation_assignment,
        start_stamp,
        start_point,
        past_end_stamp,
        past_end_point,
    ):
        print(
            f"Durational Violation: {violation_assignment} from {start_stamp} till {past_end_stamp}"
        )

    @classmethod
    def dispatch_singular_violation(cls, violation_assignment, time_stamp, time_point):
        print(f"Singular Violation at {time_stamp}: {violation_assignment}")


class OutputReceiver:
    def __init__(self, keys, sender):
        self.keys = keys
        self.sender = sender

    def update_violations(self, timestamp, timepoint, violations: list[dict]):
        pass

    def get_format(self):
        return self.keys


class SingularViolationReceiver(OutputReceiver):
    def update_violations(self, timestamp, timepoint, violations: list[dict]):
        for violation in violations:
            self.sender.dispatch_singular_violation(violation, timestamp, timepoint)


class DurationalViolationReceiver(OutputReceiver):
    def __init__(self, keys, sender):
        super().__init__(keys, sender)
        self.current_unfinished_violations = {}

    def _add_violations(self, timestamp, timepoint, violations):
        for violation in violations:
            self.current_unfinished_violations[violation] = (timestamp, timepoint)
            self.sender.dispatch_violation_started(
                dict(zip(self.keys, violation)), timestamp, timepoint
            )

    def _remove_violations(self, timestamp, timepoint, violations):
        for violation in violations:
            start_stamp, start_point = self.current_unfinished_violations.pop(violation)
            self.sender.dispatch_violation_finished(
                dict(zip(self.keys, violation)),
                start_stamp,
                start_point,
                timestamp,
                timepoint,
            )

    def update_violations(self, timestamp, timepoint, violations: list[dict]):
        """Assumes that violations are unique"""
        violations_transformed = [tuple(violation.values()) for violation in violations]
        violations_transformed = sorted(violations_transformed)
        violations_to_add = []
        erros_to_remove = []
        sorted_unfinished_keys = sorted(self.current_unfinished_violations.keys())
        while violations_transformed or sorted_unfinished_keys:
            new_violation = (
                violations_transformed.pop(0) if violations_transformed else None
            )
            unfinished_violation = (
                sorted_unfinished_keys.pop(0) if sorted_unfinished_keys else None
            )
            if new_violation == unfinished_violation:
                continue
            elif new_violation and (
                not unfinished_violation or new_violation < unfinished_violation
            ):
                violations_to_add.append(new_violation)
                sorted_unfinished_keys.insert(0, unfinished_violation)
            elif not new_violation or new_violation > unfinished_violation:
                erros_to_remove.append(unfinished_violation)
                violations_transformed.insert(0, new_violation)
        self._remove_violations(timestamp, timepoint, erros_to_remove)
        self._add_violations(timestamp, timepoint, violations_to_add)


class OutputParser:
    def __init__(self, process, output_receiver: OutputReceiver):
        self.process = process
        self.output_receiver = output_receiver
        self.matches_seperator = " ("
        self.value_seperator = ", "
        self.finished_reading_process = asyncio.Event()

    async def get_output(self):
        def get_fullfilling_assignments(assignments_str: str):
            assignments = []
            i = 0
            print("Start mapping assignments")
            while i < len(assignments_str):
                if assignments_str[i] == "(":
                    j = i + 1
                    inside_string = False  # is Inside quotes wird nicht genutzt
                    while assignments_str[j] != ")" or inside_string:
                        if assignments_str[j] == '"':
                            inside_string = not inside_string
                        j += 1
                    assignments.append(assignments_str[i + 1 : j])
                    i = j
                i += 1
            print("Finished mapping assignments with " + str(assignments))
            assignment_dicts = []
            for assignment in assignments:
                print(assignment)

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
                    print(
                        f"Free variable: {free_variable}, Value: {assignment_dict[free_variable]}"
                    )
                    i += len(self.value_seperator)
                if i < len(assignment):
                    raise Exception("Assignment contains more than the free variables")
                print(assignment_dict)
                assignment_dicts.append(assignment_dict)
            return assignment_dicts

        while True:
            line = await self.process.stdout.readline()
            if not line:
                print("process terminated")
                self.finished_reading_process.set()
                break
            decoded_line = line.decode("utf-8")
            if decoded_line[0] != "@" or decoded_line[-3:-1] == "()":
                continue

            print("Received output:")
            print(decoded_line)
            decoded_line = decoded_line[1:]
            parts = decoded_line.split(self.matches_seperator)
            if len(parts) != 3:
                raise Exception("Invalid output format")

            timestamp = float(parts[0])
            timepoint = int(re.search(r"\d+", parts[1]).group())
            fullfilling_assignments = get_fullfilling_assignments(parts[2])
            for assignment in fullfilling_assignments:
                print(f'Processed output : {timestamp}, {timepoint}, "{assignment}"')
            self.output_receiver.update_violations(
                timestamp, timepoint, fullfilling_assignments
            )


# async def get_output(
#     test_outputs,
#     output_receiver: OutputReceiver,
#     self.matches_seperator=" (",
#     self.value_seperator=", ",
# ):
#     def get_fullfilling_assignments(assignments_str: str):
#         assignments = []
#         i = 0
#         print("Start mapping assignments")
#         while i < len(assignments_str):
#             if assignments_str[i] == "(":
#                 j = i + 1
#                 inside_string = False  # is Inside quotes wird nicht genutzt
#                 while assignments_str[j] != ")" or inside_string:
#                     if assignments_str[j] == '"':
#                         inside_string = not inside_string
#                     j += 1
#                 assignments.append(assignments_str[i + 1 : j])
#                 i = j
#             i += 1
#         print("Finished mapping assignments with " + str(assignments))
#         assignment_dicts = []
#         for assignment in assignments:
#             print(assignment)
#
#             i = 0
#             assignment_dict = {}
#             for free_variable in output_receiver.get_format():
#                 if i >= len(assignment):
#                     raise Exception("Assignment does not contain all free variables")
#                 inside_string = False
#                 beginning_i = i
#                 while i < len(assignment) and (
#                     assignment[i : min(i + len(self.value_seperator), len(assignment))]
#                     != self.value_seperator
#                     or inside_string
#                 ):
#                     if assignment[i] == '"':
#                         inside_string = not inside_string
#                     i += 1
#                 assignment_dict[free_variable] = assignment[beginning_i:i]
#                 print(
#                     f"Free variable: {free_variable}, Value: {assignment_dict[free_variable]}"
#                 )
#                 i += len(self.value_seperator)
#             if i < len(assignment):
#                 raise Exception("Assignment contains more than the free variables")
#             print(assignment_dict)
#             assignment_dicts.append(assignment_dict)
#         return assignment_dicts
#
#     while True:
#         decoded_line = test_outputs.readline()
#         # decoded_line = '@1734087146.26 (time point 0): ((21, ",ag,12.\nabb"),(42, 69))\n'
#         if not decoded_line:
#             print("process terminated")
#             break
#
#         if decoded_line[0] == "@":
#             print("Received output:")
#             print(decoded_line)
#             decoded_line = decoded_line[1:-2]
#             parts = decoded_line.split(self.matches_seperator)
#             if len(parts) != 3:
#                 raise Exception("Invalid output format")
#
#             timestamp = float(parts[0])
#             timepoint = int(re.search(r"\d+", parts[1]).group())
#             fullfilling_assignments = get_fullfilling_assignments(parts[2])
#             for assignment in fullfilling_assignments:
#                 print(f'Processed output : {timestamp}, {timepoint}, "{assignment}"')
#             output_receiver.update_violations(
#                 timestamp, timepoint, fullfilling_assignments
#             )


async def main():
    await get_output(
        open(
            "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/proto.txt",
            "r",
        ),
        DurationalViolationReceiver(free_variables, ViolationDispatcher),
    )
    print("Finished")


asyncio.run(main())
# get_output(
#    open(
#        "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/proto.txt",
#        "r",
#    ),
#    DurationalViolationReceiver(free_variables, ViolationDispatcher),
# )
