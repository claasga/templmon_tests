import asyncio
import json
import requests
import websockets
import datetime
from uuid import UUID
import sys
import argparse

# testplans (get next step(inkl. switch_to_competing_patient), reset_to_state_change)
# patient_group(competing patients(patient websockets), trainer websocket, ressource_ids(geräte, personal), testplans, state_change_occured, make_next step, irgendeine art von yielding)
# setup(zwei patienten, zwei personen, ein gerät, eine patient group)
# teardown(exercise_stop(trainer consumer))
# patient_group player
# REST endpoint URLs for login views
TRAINER_LOGIN_URL = "http://localhost:8000/api/trainer/login"
PATIENT_LOGIN_URL = "http://localhost:8000/api/patient/access"

# WebSocket endpoint URLs
TRAINER_WS_URI = "ws://localhost:8000/ws/trainer"
PATIENT_WS_URI = "ws://localhost:8000/ws/patient"

BZ_MESSGERAET_ID = UUID("bec79e8b-14b2-48a1-9ea8-c678e48f352e")
REACTION_TIME = 12


class PatientGroup:
    groups = []
    simulation_end = None

    @classmethod
    def check_message(cls, websocket_instance, received_message, expected_message_type):
        received_message_type = json.loads(received_message).get("messageType")
        if received_message_type != expected_message_type:
            if received_message_type == "failure":
                raise ValueError(
                    f"WS {websocket_instance.id}: Expected message type '{expected_message_type}', got failure with {json.loads(received_message).get('message')}"
                )
            else:
                raise ValueError(
                    f"WS {websocket_instance.id}:Expected message type '{expected_message_type}', got {received_message_type}"
                )

    def __init__(
        self,
        patient_codes,
        patients_ws,
        connected_personnel_ids,
        material_id,
    ):
        self.patient_queue = list(zip(patient_codes, patients_ws))
        self._patients_step = len(patients_ws) * [0]
        self.runthrough = 1
        self.connected_personnel_ids = connected_personnel_ids
        self.material_id = material_id
        self.running_action = None
        self._INITIALIZATION = [
            self.initial_triage,  # 0
            self.assign_personnel,  # 1
            self.assign_material,  # 2
            self.start_examination,  # 3
            self.current_time,  # 4
            self.activate_next_group,  # 5
            self.await_finishing,  # 6
            self.pass_time,  # 7
            self.unassign_personnel,  # 8
            self.unassign_material,  # 9
            self.switch_to_competing_patient,  # 10
        ]
        self._LOOP = [
            self.assign_personnel,  # 11
            self.start_wrong_action,  # 12
            self.cancel_current_action,  # 13
            self.start_actual_action,  # 14
            self.activate_next_group,  # 15
            self.await_finishing,  # 16
            self.unassign_personnel,  # 17
            self.switch_to_competing_patient,  # 18
        ]
        self.STEPS = self._INITIALIZATION + self._LOOP
        self.STEPS_LOOP_START_INDEX = len(self._INITIALIZATION)

    @classmethod
    def register_for_simulation(cls, patient_group):
        cls.groups.append(patient_group)

    @classmethod
    async def execute_simulation(cls, trainer_ws):
        if not cls.groups:
            raise ValueError(
                "Simulations cannot be started without registered patient groups!"
            )

        cls.simulation_end = datetime.datetime.now() + datetime.timedelta(seconds=20.0)
        i = 0
        try:
            while datetime.datetime.now() < cls.simulation_end:
                await cls.groups[i]._execute_plan()
                i = (i + 1) % len(cls.groups)
        except Exception as e:
            print(e)
        finally:
            await trainer_ws.send(json.dumps({"messageType": "exercise-end"}))
            message = await trainer_ws.recv()
            message_type = json.loads(message).get("messageType")
            while message_type != "exercise-end":
                message = await trainer_ws.recv()
                message_type = json.loads(message).get("messageType")
                if message_type == "failure":
                    raise ValueError(
                        f"Expected message type 'exercise-end', got failure with {json.loads(message).get('message')}"
                    )
            cls.groups.clear()

    def get_current_patient_ws(self):
        return self.patient_queue[0][1]

    def get_current_patient_code(self):
        return self.patient_queue[0][0]

    async def recv_and_check_for_state_change(self, websocket_instance):
        message = await websocket_instance.recv()
        received_message_type = json.loads(message).get("messageType")
        if received_message_type == "state":
            return True, message
        return False, message

    async def _execute_plan(self):
        pause_plan = False
        while not pause_plan and datetime.datetime.now() < self.simulation_end:
            state_change, pause_plan, update_index = await self.STEPS[
                self._patients_step[0]
            ]()
            self._patients_step[update_index] = (
                self._patients_step[update_index] + 1
                if self._patients_step[update_index] + 1 < len(self.STEPS)
                else self.STEPS_LOOP_START_INDEX
            )
            if state_change:
                if self.running_action:
                    await self.cancel_current_action()
                self._patients_step[update_index] = 0
            print(f"next step is now {self._patients_step[0]}", flush=True)

    async def skip_until_message(self, websocket_instance, message_type):
        state_change, message = await self.recv_and_check_for_state_change(
            websocket_instance
        )
        # message = await
        received_message_type = json.loads(message).get("messageType")
        print(
            f"WS({websocket_instance.id} received {received_message_type}", flush=True
        )
        while received_message_type != message_type:
            if received_message_type == "failure":
                raise ValueError(
                    f"WS {websocket_instance.id}: Expected message type '{message_type}', got failure with {json.loads(message).get('message')}"
                )
            temp_state_change, message = await self.recv_and_check_for_state_change(
                websocket_instance
            )
            state_change = state_change or temp_state_change
            received_message_type = json.loads(message).get("messageType")
            print(
                f"WS({websocket_instance.id} received {received_message_type}",
                flush=True,
            )
        return state_change, message

    async def skip_until_get_action_id(self):

        state_change, message = await self.skip_until_message(
            self.get_current_patient_ws(), "action-confirmation"
        )
        self.check_message(
            self.get_current_patient_ws(),
            message,
            "action-confirmation",
        )
        return state_change, json.loads(message).get("actionId")

    async def skip_until_measurement_finished(self):
        return await self.skip_until_message(
            self.get_current_patient_ws(), "patient-measurement-finished"
        )[0]

    async def initial_triage(self):
        state_change = False
        if self.get_current_patient_code() == "1001":

            print(f"Triagiere ws {self.get_current_patient_ws().id}")
            await self.get_current_patient_ws().send(
                json.dumps(
                    {"messageType": "triage", "triage": str(self.runthrough % 3)}
                )
            )
            state_change = await self.skip_until_measurement_finished()
        return state_change, False, 0

    async def assign_personnel(self):
        state_change = False
        for personnel_id in self.connected_personnel_ids:
            await self.get_current_patient_ws().send(
                json.dumps(
                    {"messageType": "personnel-assign", "personnelId": personnel_id}
                )
            )
            temp_state_change = await self.skip_until_measurement_finished()
            state_change = state_change or temp_state_change
        return state_change, False, 0

    async def assign_material(self):
        await self.get_current_patient_ws().send(
            json.dumps(
                {"messageType": "material-assign", "materialId": self.material_id}
            )
        )
        state_change = await self.skip_until_measurement_finished()
        return state_change, False, 0

    async def probe_messages(
        self, websocket_instance: websockets.WebSocketClientProtocol
    ):
        print("Probing:")
        for i in range(15):
            message = await websocket_instance.recv()
            received_message_type = json.loads(message).get("messageType")
            print(received_message_type)
            if received_message_type == "action-list":
                print(json.loads(message).get("actions"))
            await asyncio.sleep(0.1)

    async def start_action(self, action_name):
        await self.get_current_patient_ws().send(
            json.dumps({"messageType": "action-add", "actionName": action_name})
        )
        state_change, self.running_action = await self.skip_until_get_action_id()
        temp_state_change = await self.skip_until_measurement_finished()
        state_change = state_change or temp_state_change
        return state_change, False, 0

    async def start_examination(self):
        return await self.start_action("Blutzucker analysieren")

    async def switch_to_competing_patient(self):
        rotate = lambda list_type: list_type.append(list_type.pop(0))
        rotate(self.patient_queue)
        rotate(self._patients_step)
        return False, False, -1

    async def await_finishing(self):
        some_list = [1, 2, 3, 4, 5]
        action_finished = False
        state_change = False
        while not action_finished:
            temp_state_change, action_list = await self.skip_until_message(
                self.get_current_patient_ws(), "action-list"
            )
            state_change = state_change or temp_state_change
            action_list = json.loads(action_list).get("actions")
            running_action = next(
                (
                    action
                    for action in action_list
                    if action.get("actionId") == self.running_action
                ),
                {"actionStatus": ""},
            )
            action_finished = running_action.get("actionStatus") == "FI"
        self.running_action = None
        return state_change, False, 0

    async def current_time(self):
        self.examination_start = datetime.datetime.now()
        return False, False, 0

    async def activate_next_group(self):
        return False, True, 0

    async def pass_time(self):
        time_to_pass = 1.5
        timedelta = (datetime.datetime.now() - self.examination_start).total_seconds()
        if timedelta < time_to_pass:
            await asyncio.sleep(time_to_pass - timedelta)
        return False, False, 0

    async def unassign_personnel(self):
        state_change = False
        for personnel_id in self.connected_personnel_ids:
            await self.get_current_patient_ws().send(
                json.dumps(
                    {"messageType": "personnel-release", "personnelId": personnel_id}
                )
            )
            temp_state_change = await self.skip_until_measurement_finished()
            state_change = state_change or temp_state_change
        return state_change, False, 0

    async def unassign_material(self):
        await self.get_current_patient_ws().send(
            json.dumps(
                {"messageType": "material-release", "materialId": self.material_id}
            )
        )
        state_change = await self.skip_until_measurement_finished()
        return state_change, False, 0

    async def start_wrong_action(self):
        return await self.start_action("ZVK")

    async def cancel_current_action(self):
        await self.get_current_patient_ws().send(
            json.dumps(
                {"messageType": "action-cancel", "actionId": self.running_action}
            )
        )
        state_change = await self.skip_until_measurement_finished()
        self.running_action = None
        return state_change, False, 0

    async def start_actual_action(self):
        return await self.start_action("Turniquet")


class PatientGroupTemplmonActive(PatientGroup):
    def __init__(
        self,
        patient_codes,
        patients_ws,
        connected_personnel_ids,
        material_id,
        trainer_ws,
    ):
        super().__init__(
            patient_codes, patients_ws, connected_personnel_ids, material_id
        )
        self.trainer_ws = trainer_ws

    async def skip_until_measurement_finished(self):
        r_1, r_2 = await asyncio.gather(
            self.skip_until_message(
                self.get_current_patient_ws(), "patient-measurement-finished"
            ),
            self.skip_until_message(self.trainer_ws, "trainer-measurement-finished"),
        )
        return r_1[0] or r_2[0]


def login_trainer(username, password):
    payload = {"username": username, "password": password}
    response = requests.post(TRAINER_LOGIN_URL, json=payload)
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Trainer logged in, token: {token}")
        return token
    else:
        print("Trainer login failed:", response.text)
        return None


def login_patient(exerciseId, patientId):
    payload = {"exerciseId": exerciseId, "patientId": patientId}
    response = requests.post(PATIENT_LOGIN_URL, json=payload)
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Patient logged in, token: {token}")
        return token
    else:
        print("Patient login failed:", response.text)
        return None


async def generate_trainer_websocket(token):
    websocket = await websockets.connect(TRAINER_WS_URI + "/?token=" + token)
    return websocket


async def generate_patient_websocket(token):
    websocket = await websockets.connect(PATIENT_WS_URI + "/?token=" + token)
    exercise = await websocket.recv()
    available_actions = await websocket.recv()
    available_patients = await websocket.recv()
    state = await websocket.recv()
    return websocket


async def setup_exercise(
    trainer_ws: websockets.WebSocketClientProtocol, patient_count, max_area_size
):
    if patient_count % 2 != 0:
        raise ValueError("patient count must always be multiple of two!")
    if max_area_size < 2:
        raise ValueError("max_area_size must be at least 2!")
    max_area_size -= max_area_size % 2
    available_patients_json = await trainer_ws.recv()
    available_patients = json.loads(available_patients_json)
    print(available_patients.get("availablePatients"))
    available_materials_json = await trainer_ws.recv()
    available_materials = json.loads(available_materials_json)
    print(available_materials.get("availableMaterials"))

    await trainer_ws.send(json.dumps({"messageType": "exercise-create"}))
    exercise_json = await trainer_ws.recv()
    exercise = json.loads(exercise_json)
    print(exercise)
    await trainer_ws.send(json.dumps({"messageType": "area-add"}))
    exercise_json = await trainer_ws.recv()
    exercise = json.loads(exercise_json)
    print(exercise)
    idle_areID = int(exercise.get("exercise").get("areas")[-1].get("areaId"))
    await trainer_ws.send(
        json.dumps(
            {"messageType": "area-rename", "areaId": idle_areID, "areaName": "X"}
        )
    )
    exercise_json = await trainer_ws.recv()
    await trainer_ws.send(
        json.dumps(
            {
                "messageType": "patient-add",
                "areaId": idle_areID,
                "patientName": f"Idle Patient {idle_areID}",
                "code": 1005,
            }
        )
    )
    exercise_json = await trainer_ws.recv()
    patient_ids = []
    exercise_json = None
    for i in range(0, int(patient_count / 2)):
        if i % (interval := int(max_area_size / 2)) == 0:
            await trainer_ws.send(json.dumps({"messageType": "area-add"}))
            exercise_json = await trainer_ws.recv()
            exercise = json.loads(exercise_json)
            print(exercise)
            areaID = int(exercise.get("exercise").get("areas")[-1].get("areaId"))
            print(f"area id is : {areaID}")
        await trainer_ws.send(
            json.dumps(
                {
                    "messageType": "patient-add",
                    "areaId": areaID,
                    "patientName": f"Good Patient {areaID}.{i % interval}",
                    "code": 1001,
                }
            )
        )
        exercise_json = await trainer_ws.recv()
        await trainer_ws.send(
            json.dumps(
                {
                    "messageType": "patient-add",
                    "areaId": areaID,
                    "patientName": f"Bad Patient {areaID}.{i % interval}",
                    "code": 1005,
                }
            )
        )
        exercise_json = await trainer_ws.recv()
        await trainer_ws.send(
            json.dumps(
                {
                    "messageType": "personnel-add",
                    "areaId": areaID,
                    "personnelName": f"Helper {areaID}.{i % interval}.1",
                }
            )
        )
        exercise_json = await trainer_ws.recv()
        await trainer_ws.send(
            json.dumps(
                {
                    "messageType": "personnel-add",
                    "areaId": areaID,
                    "personnelName": f"Helper {areaID}.{i % interval}.2",
                }
            )
        )
        exercise_json = await trainer_ws.recv()
        await trainer_ws.send(
            json.dumps(
                {
                    "messageType": "material-add",
                    "areaId": areaID,
                    "materialName": "BZ-Messgerät",
                }
            )
        )
        exercise_json = await trainer_ws.recv()
    exercise = json.loads(exercise_json).get("exercise")
    print(exercise)
    areas = exercise.get("areas")
    personnel_ids = []
    material_ids = []
    for area in areas:
        patient_ids.extend(
            [patient.get("patientId") for patient in area.get("patients")]
        )
        personnel_ids.extend(
            [personnel.get("personnelId") for personnel in area.get("personnel")]
        )
        material_ids.extend(
            [material.get("materialId") for material in area.get("material")]
        )

    print(patient_ids)
    return patient_ids, personnel_ids, material_ids, exercise.get("exerciseId")


class TestCases:
    PERSONNEL_CHECK = "pc"
    SYMPTOM_COMBINATION = "sc"
    PERSONNEL_PRIORITIZATION = "pp"
    TRIAGE_GOAL = "tg"
    FILTER = "ft"
    BERLIN = "bl"


async def configure_templates(
    trainer_ws: websockets.WebSocketClientProtocol, templates_to_use: list[TestCases]
):
    templates = {
        TestCases.PERSONNEL_CHECK: [
            {
                "type": "personnel_check",
                "name": "beq_two_rule",
                "configuration": {"operator": ">=", "personnel_count": 2},
            },
            {
                "type": "personnel_check",
                "name": "smaller_two_rule",
                "configuration": {"operator": "<", "personnel_count": 2},
            },
        ],
        TestCases.SYMPTOM_COMBINATION: [
            {
                "type": "symptom_combination",
                "name": "special_tourniquet",
                "configuration": {
                    "action": "Turniquet",
                    "timeframe": REACTION_TIME,
                    "vital_parameters": {"circulation": ("<=", 83)},
                    "examination_results": {"Blutzucker analysieren": "BZ:_125"},
                    "fullfillment": False,
                },
            },
            {
                "type": "symptom_combination",
                "name": "special_tourniquet",
                "configuration": {
                    "action": "Turniquet",
                    "timeframe": REACTION_TIME,
                    "vital_parameters": {"circulation": ("<=", 83)},
                    "examination_results": {"Blutzucker analysieren": "BZ:_125"},
                    "fullfillment": True,
                },
            },
        ],
        TestCases.PERSONNEL_PRIORITIZATION: [
            {
                "type": "personnel_prioritization",
                "name": "1002_is_worse",
                "configuration": {
                    "vital_sign_p1": "circulation",
                    "operator_p1": "<=",
                    "value_p1": 83,
                    "personnel_count_p1": 1,
                    "vital_sign_p2": "circulation",
                    "operator_p2": ">=",
                    "value_p2": 94,
                    "personnel_count_p2": 2,
                },
            }
        ],
        TestCases.TRIAGE_GOAL: [
            {
                "type": "triage_goal",
                "name": "yellow_1002",
                "configuration": {
                    "patient_id": 3,
                    "target_time": REACTION_TIME - 1,
                    "target_level": "Yellow",
                    "fullfillment": True,
                },
            },
            {
                "type": "triage_goal",
                "name": "yellow_1002",
                "configuration": {
                    "patient_id": 3,
                    "target_time": REACTION_TIME - 1,
                    "target_level": "Yellow",
                    "fullfillment": True,
                },
            },
        ],
        TestCases.FILTER: [
            {
                "type": "aliveness_check",
                "name": "who_is_there",
                "configuration": {"fullfillment": True},
            },
            {
                "type": "aliveness_check",
                "name": "rise_from_the_ashes",
                "configuration": {"fullfillment": False},
            },
            {
                "type": "interacted_check",
                "name": "mamas_favourite_boy",
                "configuration": {"fullfillment": True},
            },
            {
                "type": "interacted_check",
                "name": "lonely",
                "configuration": {"fullfillment": False},
            },
            {
                "type": "triaged_check",
                "name": "triaged",
                "configuration": {"fullfillment": True},
            },
            {
                "type": "triaged_check",
                "name": "untriaged",
                "configuration": {"fullfillment": False},
            },
        ],
        TestCases.BERLIN: [
            {"type": "berlin_algorithm", "name": "wrong", "configuration": {}}
        ],
    }
    for template in templates_to_use:
        for sub_template in templates[template]:
            await trainer_ws.send(
                json.dumps({"messageType": "log-rule-add", **sub_template})
            )


async def start_exercise(
    trainer_ws: websockets.WebSocketClientProtocol,
    patients_ws: list[websockets.WebSocketClientProtocol],
):
    await trainer_ws.send(json.dumps({"messageType": "exercise-start"}))
    exercise_start = await trainer_ws.recv()
    for patient_ws in patients_ws:
        exercise_start = await patient_ws.recv()
        action_list = await patient_ws.recv()


async def template_test(patient_count, area_size, templates_to_use=None):
    # Login via HTTP to get tokens before WebSocket connections
    PatientGroupClass = (
        PatientGroup if not templates_to_use else PatientGroupTemplmonActive
    )
    trainer_name = f"trainer_created_{datetime.datetime.now()}"
    print(trainer_name)
    trainer_token = login_trainer(trainer_name, "trainer_password")

    # Check if login was successful
    if not trainer_token:
        raise ConnectionRefusedError("Login failed for one or more clients; aborting")
    trainer_ws = await generate_trainer_websocket(trainer_token)
    patient_ids, personnel_ids, material_ids, exercise_id = await setup_exercise(
        trainer_ws, patient_count, area_size
    )
    if templates_to_use:
        await configure_templates(trainer_ws, templates_to_use)
    tokens = [login_patient(exercise_id, patient_id) for patient_id in patient_ids]
    patients_ws = await asyncio.gather(
        *[generate_patient_websocket(token) for token in tokens]
    )
    for i in range(len(material_ids)):
        i_1 = i * 2
        i_2 = (i * 2) + 1
        args = [
            ["1001", "1005"] * (patient_count // 2),
            [patients_ws[i_1], patients_ws[i_2]],
            [personnel_ids[i_1], personnel_ids[i_2]],
            material_ids[i],
        ]
        if templates_to_use:
            args.append(trainer_ws)
        patient_group_instance = PatientGroupClass(*args)
        PatientGroupClass.register_for_simulation(patient_group_instance)
    await start_exercise(trainer_ws, patients_ws)
    try:
        await PatientGroupClass.execute_simulation(trainer_ws)
    except Exception as e:
        print(e)
        raise
    return True


if __name__ == "__main__":
    # asyncio.run(template_test([(2, 2), (10, 2), (30, 2)]))
    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description="Run the template test script.")
    parser.add_argument("patient_count", type=int, help="Number of patients.")
    parser.add_argument(
        "--test_cases",
        type=str,
        default="",
        help="Comma-separated list of test cases (optional).",
    )
    args = parser.parse_args()

    # Extract arguments
    patient_count = args.patient_count
    test_cases = [test_case.strip() for test_case in args.test_cases.split(",")]
    if test_cases:
        asyncio.run(template_test(patient_count, 10, test_cases))
    else:
        asyncio.run(template_test(patient_count, 10))
