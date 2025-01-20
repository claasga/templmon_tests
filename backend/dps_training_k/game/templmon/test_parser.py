import re
import asyncio

free_variables = ["personnel_id", "patient_id"]


class TestSender:
    @classmethod
    def dispatch_error_started(cls, error_assignment, start_stamp, start_point):
        print(f"Durational Error started at {start_stamp}: {error_assignment}")

    @classmethod
    def dispatch_error_finished(
        cls, error_assignment, start_stamp, start_point, past_end_stamp, past_end_point
    ):
        print(
            f"Durational Error: {error_assignment} from {start_stamp} till {past_end_stamp}"
        )

    @classmethod
    def dispatch_singular_error(cls, error_assignment, time_stamp, time_point):
        print(f"Singular Error at {time_stamp}: {error_assignment}")


class OutputReceiver:
    def __init__(self, keys, sender):
        self.keys = keys
        self.sender = sender

    def update_errors(self, timestamp, timepoint, errors: list[dict]):
        pass

    def get_format(self):
        return self.keys


class SingularErrorReceiver(OutputReceiver):
    def update_errors(self, timestamp, timepoint, errors: list[dict]):
        for error in errors:
            self.sender.dispatch_singular_error(error, timestamp, timepoint)


class DurationalErrorReceiver(OutputReceiver):
    def __init__(self, keys, sender):
        super().__init__(keys, sender)
        self.current_unfinished_errors = {}

    def _add_errors(self, timestamp, timepoint, errors):
        for error in errors:
            self.current_unfinished_errors[error] = (timestamp, timepoint)
            self.sender.dispatch_error_started(
                dict(zip(self.keys, error)), timestamp, timepoint
            )

    def _remove_errors(self, timestamp, timepoint, errors):
        for error in errors:
            start_stamp, start_point = self.current_unfinished_errors.pop(error)
            self.sender.dispatch_error_finished(
                dict(zip(self.keys, error)),
                start_stamp,
                start_point,
                timestamp,
                timepoint,
            )

    def update_errors(self, timestamp, timepoint, errors: list[dict]):
        """Assumes that errors are unique"""
        errors_transformed = [tuple(error.values()) for error in errors]
        errors_transformed = sorted(errors_transformed)
        errors_to_add = []
        erros_to_remove = []
        sorted_unfinished_keys = sorted(self.current_unfinished_errors.keys())
        while errors_transformed or sorted_unfinished_keys:
            new_error = errors_transformed.pop(0) if errors_transformed else None
            unfinished_error = (
                sorted_unfinished_keys.pop(0) if sorted_unfinished_keys else None
            )
            if new_error == unfinished_error:
                continue
            elif new_error and (not unfinished_error or new_error < unfinished_error):
                errors_to_add.append(new_error)
                sorted_unfinished_keys.insert(0, unfinished_error)
            elif not new_error or new_error > unfinished_error:
                erros_to_remove.append(unfinished_error)
                errors_transformed.insert(0, new_error)
        self._remove_errors(timestamp, timepoint, erros_to_remove)
        self._add_errors(timestamp, timepoint, errors_to_add)


def get_output(
    test_outputs,
    output_receiver: OutputReceiver,
    matches_seperator=" (",
    value_seperator=", ",
):
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
            for free_variable in output_receiver.get_format():
                if i >= len(assignment):
                    raise Exception("Assignment does not contain all free variables")
                inside_string = False
                beginning_i = i
                while i < len(assignment) and (
                    assignment[i : min(i + len(value_seperator), len(assignment))]
                    != value_seperator
                    or inside_string
                ):
                    if assignment[i] == '"':
                        inside_string = not inside_string
                    i += 1
                assignment_dict[free_variable] = assignment[beginning_i:i]
                print(
                    f"Free variable: {free_variable}, Value: {assignment_dict[free_variable]}"
                )
                i += len(value_seperator)
            if i < len(assignment):
                raise Exception("Assignment contains more than the free variables")
            print(assignment_dict)
            assignment_dicts.append(assignment_dict)
        return assignment_dicts

    while True:
        decoded_line = test_outputs.readline()
        # decoded_line = '@1734087146.26 (time point 0): ((21, ",ag,12.\nabb"),(42, 69))\n'
        if not decoded_line:
            print("process terminated")
            break

        if decoded_line[0] == "@":
            print("Received output:")
            print(decoded_line)
            decoded_line = decoded_line[1:-2]
            parts = decoded_line.split(matches_seperator)
            if len(parts) != 3:
                raise Exception("Invalid output format")

            timestamp = float(parts[0])
            timepoint = int(re.search(r"\d+", parts[1]).group())
            fullfilling_assignments = get_fullfilling_assignments(parts[2])
            for assignment in fullfilling_assignments:
                print(f'Processed output : {timestamp}, {timepoint}, "{assignment}"')
            output_receiver.update_errors(timestamp, timepoint, fullfilling_assignments)
        # asyncio.sleep(1)


async def main():
    await get_output(
        open(
            "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/test.txt",
            "r",
        ),
        OutputReceiver(),
    )
    print("Finished")


# asyncio.run(main())
get_output(
    open(
        "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/test.txt",
        "r",
    ),
    SingularErrorReceiver(free_variables, TestSender),
)
