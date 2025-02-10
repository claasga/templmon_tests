if __name__ == "__main__":

    class Whatever:
        def __init__(self, same_violation_keys):
            self.current_unfinished_violations = {}
            if not same_violation_keys:
                raise ValueError(
                    "len(same_violation_keys)==0! Duration of errors for violations without defintion of violation instance cannot be calculated"
                )
            self.same_violation_keys = same_violation_keys

        def _add_violations(self, timestamp, timepoint, filtered_violations):
            for violation in filtered_violations:
                self.current_unfinished_violations[violation] = (timestamp, timepoint)
            print(f"violations to add : {filtered_violations}")

        def _remove_violations(self, timestamp, timepoint, filtered_violations):
            for violation in filtered_violations:
                start_stamp, start_point = self.current_unfinished_violations.pop(
                    violation
                )
            print(f"violations to remove : {filtered_violations}")

        def _change_violations(self, timestamp, timepoint, violations):
            print(f"violations to change : {violations}")

        def update_violations(self, timestamp, timepoint, violations: list[dict]):
            """Assumes that violations are unique. For MonPoly they are"""
            unfinished_keys = list(self.current_unfinished_violations.keys())
            if len(violations) == 0:
                self._remove_violations(timestamp, timepoint, unfinished_keys)
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
            violations_comparable = [
                tuple(violation.values()) for violation in violations
            ]
            violations_filtered, violations_comparable = [
                list(group)
                for group in zip(
                    *sorted(zip(violations_filtered, violations_comparable))
                )
            ]
            violations_to_add = []
            violations_to_remove = []
            violations_to_change = []

            while True:
                new_violation = (
                    violations_filtered.pop(0) if violations_filtered else None
                )

                unfinished_violation = (
                    unfinished_keys.pop(0) if unfinished_keys else None
                )
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
            self._remove_violations(timestamp, timepoint, violations_to_remove)
            self._add_violations(timestamp, timepoint, violations_to_add)
            self._change_violations(timestamp, timepoint, violations_to_change)

    o = Whatever(["patient"])
    o.update_violations(10, 1, [{"patient": "5", "personnel_count": "2"}])
    o.update_violations(
        11,
        2,
        [
            {"patient": "5", "personnel_count": "4"},
            {"patient": "4", "personnel_count": "4"},
            {"patient": "6", "personnel_count": "4"},
        ],
    )
    o.update_violations(23, 3, [{"patient": "4", "personnel_count": "2"}])
    o.update_violations(25, 4, [])

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
                if (asgnm := assignments_str[i + 1 : j]) and asgnm != "":
                    assignments.append(asgnm)
                i = j
            i += 1
        if not assignments:
            return assignments
        print("Finished mapping assignments with " + str(assignments))
        assignment_dicts = []
        for assignment in assignments:
            print(assignment)

            i = 0
            assignment_dict = {}
            for free_variable in ["patient", "personnel_count"]:
                if i >= len(assignment):
                    raise Exception("Assignment does not contain all free variables")
                inside_string = False
                beginning_i = i
                while i < len(assignment) and (
                    assignment[i : min(i + len(","), len(assignment))] != ","
                    or inside_string
                ):
                    if assignment[i] == '"':
                        inside_string = not inside_string
                    i += 1
                assignment_dict[free_variable] = assignment[beginning_i:i]
                print(
                    f"Free variable: {free_variable}, Value: {assignment_dict[free_variable]}"
                )
                i += len(",")
            if i < len(assignment):
                raise Exception("Assignment contains more than the free variables")
            print(assignment_dict)
            assignment_dicts.append(assignment_dict)
        return assignment_dicts

    print(get_fullfilling_assignments("()"))
