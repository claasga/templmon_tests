class RuleProperty:
    class MPT:
        string = "string"
        integer = "integer"
        float = "float"

    class NameType:
        def __init__(self, name, type):
            self.name = name
            self.type = type

        def __str__(self):
            # return self.name
            return "RuleProperty: " + self.name

        def __iter__(self):
            return iter((self.name, self.type))

    LOCATION = NameType("location", MPT.string)
    OLD_LOCATION = NameType(f"{LOCATION.name}_old", MPT.string)
    NEW_LOCATION = NameType(f"{LOCATION.name}_new", MPT.string)
    PERSONNEL = NameType("personnel", MPT.string)
    PATIENT = NameType("patient", MPT.string)
    ACTION = NameType("action", MPT.string)
    EXAMINATION = NameType("examination", MPT.string)
    RESULT = NameType("result", MPT.string)
    DEVICE = NameType("device", MPT.string)
    TRIAGE = NameType("triage", MPT.string)
    INJURY_LEVEL = NameType("injury_level", MPT.string)
    AIRWAY = NameType("airway", MPT.float)
    BREATHING = NameType("breathing", MPT.float)
    CIRCULATION = NameType("circulation", MPT.float)
    BEWUSSTSEIN = NameType("consciousness", MPT.string)
    PUPILLEN = NameType("pupils", MPT.string)
    PSYCHE = NameType("psyche", MPT.string)
    HAUT = NameType("skin", MPT.string)
    DEAD = NameType("dead", MPT.string)
    UNKNOWN = NameType("unknown", MPT.string)


class LogType:

    _BASE_VARIABLES = []
    MONPOLY_NAME = None  # Expecting list with unique items

    def __init__(self):
        self._variables = {var.name: var.name for var in self._BASE_VARIABLES}

    def mfotl(self):
        return f'{self.MONPOLY_NAME}({",".join(self._variables.values())})'

    def bind(self, keys=[], include=True):
        if not include:
            keys = [var for var in self._variables.keys() if var not in keys]
        keys = [key for key in keys if self.get_variable(key)[0] != '"']
        return ", ".join([self.get_variable(var) for var in keys])

    def compare_values_mfotl(self, key_values):
        def quotify(value):
            return f'"{value}"' if isinstance(value, str) else value

        return " AND ".join(
            [
                f"{self.get_variable(key)} = {quotify(value)}"
                for key, value in key_values.items()
                if self.get_variable(key)[0] != '"'
            ]
        )

    @classmethod
    def bulk_create(cls, amount, matching_variables={}, start_id=1):
        objects = [cls() for i in range(amount)]
        for i in range(amount):
            obj = objects[i]
            for var in obj._variables:
                if var in matching_variables:
                    obj.set_variable(var, matching_variables[var])
                else:
                    obj.set_variable(var, f"{var}_{i + start_id}")
        return objects

    @classmethod
    def monpoly_representation(cls):
        return f"{cls.MONPOLY_NAME}({', '.join([var.type for var in cls._BASE_VARIABLES])})"

    @classmethod
    def log(cls, *args):
        raise NotImplementedError

    def match(self, others, matching_variables):
        for other in others:
            for var in matching_variables:
                other.set_variable(var, self.get_variable(var))

    def get_variable(self, key: str):
        if key in self._variables:
            return self._variables[key]
        raise KeyError(f"Variable '{key}' not found in {self.__class__.__name__}")

    def set_variable(self, key: str, value):
        if key not in self._variables:
            raise KeyError(f"Variable '{key}' not found in {self.__class__.__name__}")

        self._variables[key] = value

    @classmethod
    def _monpolify_args(cls, args):
        for arg, var in zip(args, cls._BASE_VARIABLES):
            if var.type == RuleProperty.MPT.string:
                arg = f'"{arg}"'
            elif isinstance(arg, bool):
                arg = str(arg).upper()


class AssignedPersonnel(LogType):
    _BASE_VARIABLES = [RuleProperty.PERSONNEL, RuleProperty.PATIENT]
    MONPOLY_NAME = "assigned_personnel"

    @classmethod
    def log(cls, personnel, patient):
        cls._monpolify_args([personnel, patient])
        return f"{cls.MONPOLY_NAME}({personnel}, {patient})"


class UnassignedPersonnel(LogType):
    _BASE_VARIABLES = [RuleProperty.PERSONNEL]
    MONPOLY_NAME = "unassigned_personnel"

    @classmethod
    def log(cls, personnel):
        cls._monpolify_args([personnel])
        return f"{cls.MONPOLY_NAME}({personnel})"


class ChangedState(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.AIRWAY,
        RuleProperty.CIRCULATION,
        RuleProperty.DEAD,
    ]
    MONPOLY_NAME = "changed_state"

    @classmethod
    def log(cls, patient, airway, circulation, dead: bool):
        cls._monpolify_args([patient, airway, circulation, dead])
        return f"{cls.MONPOLY_NAME}({patient}, {airway}, {circulation}, {dead})"


class PatientArrived(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.LOCATION,
        RuleProperty.TRIAGE,
        RuleProperty.INJURY_LEVEL,
    ]
    MONPOLY_NAME = "patient_arrived"

    @classmethod
    def log(cls, patient, location, triage, injury_level):
        cls._monpolify_args([patient, location, triage, injury_level])
        return f"{cls.MONPOLY_NAME}({patient}, {location}, {triage}, {injury_level})"


class PatientRelocated(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.OLD_LOCATION,
        RuleProperty.NEW_LOCATION,
    ]
    MONPOLY_NAME = "patient_relocated"

    @classmethod
    def log(cls, patient, old_location, new_location):
        cls._monpolify_args([patient, old_location, new_location])
        return f"{cls.MONPOLY_NAME}({patient}, {old_location}, {new_location})"


class ExaminationResult(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.EXAMINATION,
        RuleProperty.RESULT,
    ]
    MONPOLY_NAME = "examination_result"

    @classmethod
    def log(cls, patient, examination, result):
        cls._monpolify_args([patient, examination, result])
        return f"{cls.MONPOLY_NAME}({patient}, {examination}, {result})"


class ActionStarted(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.ACTION,
    ]
    MONPOLY_NAME = "action_started"

    @classmethod
    def log(cls, patient, action):
        cls._monpolify_args([patient, action])
        return f"{cls.MONPOLY_NAME}({patient}, {action})"


class ActionCanceled(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.ACTION,
    ]
    MONPOLY_NAME = "action_canceled"

    @classmethod
    def log(cls, patient, action):
        cls._monpolify_args([patient, action])
        return f"{cls.MONPOLY_NAME}({patient}, {action})"


class ActionFinished(LogType):
    _BASE_VARIABLES = [
        RuleProperty.PATIENT,
        RuleProperty.ACTION,
    ]
    MONPOLY_NAME = "action_finished"

    @classmethod
    def log(cls, patient, action):
        cls._monpolify_args([patient, action])
        return f"{cls.MONPOLY_NAME}({patient}, {action})"


def generate_monpoly_signature(file_path):
    """:file_path: exclude the type of file, e.g. /path/to/file"""

    def get_all_subclasses(cls):
        subclasses = set(cls.__subclasses__())
        for subclass in cls.__subclasses__():
            subclasses.update(get_all_subclasses(subclass))
        return subclasses

    subclasses = get_all_subclasses(LogType)
    with open(f"{file_path}.sig", "w") as f:
        for subclass in subclasses:
            f.write(subclass.monpoly_representation() + "\n")


if __name__ == "__main__":
    assigned_personnel = ChangedState()
    print(
        assigned_personnel.get_variable(RuleProperty.CIRCULATION.name)
    )  # Output: breathing
    assigned_personnel.set_variable(RuleProperty.CIRCULATION.name, "selected")
    print(
        assigned_personnel.get_variable(RuleProperty.CIRCULATION.name)
    )  # Output: selected
    print(assigned_personnel.mfotl())  # Output: patient,airway,selected,aliveness
    print(
        assigned_personnel.monpoly_representation()
    )  # Output: changed_state(string, float, float, string)
    import os

    generate_monpoly_signature(
        os.path.join(os.path.dirname(__file__), "signature_test")
    )
    print(assigned_personnel.bind(["patient", "dead"]))  # Output: airway, selected
    bulk = ChangedState.bulk_create(
        3, matching_variables={RuleProperty.PATIENT.name: "special_name"}
    )
    for e in bulk:
        print(e.mfotl())
    print(
        assigned_personnel.compare_values_mfotl(
            {RuleProperty.CIRCULATION.name: 1.7, RuleProperty.DEAD.name: "TRUE"}
        )
    )
    print(assigned_personnel.compare_values_mfotl({RuleProperty.CIRCULATION.name: 1.7}))
