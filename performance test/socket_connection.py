import asyncio
import json
import requests
import websockets
import random
import datetime
from uuid import UUID

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


class PatientGroup:
    groups = []
    simulation_end = None

    @classmethod
    async def receive_and_check_message(cls, websocket_instance, message_type):
        message = await websocket_instance.recv()
        received_message_type = json.loads(message).get("messageType")
        if received_message_type != message_type:
            if received_message_type == "failure":
                raise ValueError(
                    f"WS {websocket_instance.id}: Expected message type '{message_type}', got failure with {json.loads(message).get('message')}"
                )
            else:
                raise ValueError(
                    f"WS {websocket_instance.id}:Expected message type '{message_type}', got {received_message_type}"
                )

    @classmethod
    async def global_consume_message_type(cls, message_type):
        for group in cls.groups:
            for ws in [patient_ws for _, patient_ws in group.patient_queue]:
                await cls.receive_and_check_message(ws, message_type)
            if message_type == "exercise":
                await cls.receive_and_check_message(group.trainer_ws, message_type)

    def __init__(
        self,
        patient_codes,
        patients_ws,
        trainer_ws,
        connected_personnel_ids,
        material_id,
    ):
        self.patient_queue = list(zip(patient_codes, patients_ws))
        self._patients_step = len(patients_ws) * [0]
        self.runthrough = 1
        self.trainer_ws = trainer_ws
        self.connected_personnel_ids = connected_personnel_ids
        self.material_id = material_id
        self._INITIALIZATION = [
            self.initial_triage,
            self.assign_personnel,
            self.assign_material,
            self.start_examination,
            # self.activate_next_group,
            # self.await_finishing,
            # self.pass_time,
            # self.unassign_personnel,
            # self.switch_to_competing_patient,
        ]
        self._LOOP = [
            self.assign_personnel,
            # self.start_wrong_action,
            # self.cancel_action,
            # self.start_actual_action,
            # self.activate_next_group,
            # self.await_finishing,
            # self.unassign_personnel,
            # self.switch_to_competing_patient,
        ]
        self.STEPS = self._INITIALIZATION + self._LOOP
        self.STEPS_LOOP_START_INDEX = len(self._INITIALIZATION)

    @classmethod
    def register_for_simulation(cls, patient_group):
        cls.groups.append(patient_group)

    @classmethod
    async def execute_simulation(cls):
        if not cls.groups:
            raise ValueError(
                "Simulations cannot be started without registered patient groups!"
            )

        cls.simulation_end = datetime.datetime.now() + datetime.timedelta(minutes=10.0)
        await cls.groups[0]._execute_plan()

    async def _execute_plan(self):

        while datetime.datetime.now() < self.simulation_end:
            await self.STEPS[self._patients_step[0]]()
            self._patients_step[0] = (
                self._patients_step[0] + 1
                if self._patients_step[0] + 1 < len(self.STEPS)
                else self.STEPS_LOOP_START_INDEX
            )
            print(f"next step is now {self._patients_step[0]}")

    async def finish_measurements(self, patient_ws):
        await self.receive_and_check_message(patient_ws, "patient-measurement-finished")
        print("patient measurement finished")
        await self.receive_and_check_message(
            self.trainer_ws, "trainer-measurement-finished"
        )
        print("trainer measurement finished")

    async def initial_triage(self):
        patient_code, patient_ws = self.patient_queue[0]
        if patient_code == "1001":
            await patient_ws.send(
                json.dumps({"messageType": "triage", "triage": self.runthrough % 3})
            )
            await self.global_consume_message_type("exercise")
            await self.finish_measurements(patient_ws)

    async def assign_personnel(self):
        patient_code, patient_ws = self.patient_queue[0]
        for personnel_id in self.connected_personnel_ids:
            await patient_ws.send(
                json.dumps(
                    {"messageType": "personnel-assign", "personnelId": personnel_id}
                )
            )
            print(f"WS {patient_ws.id}: assigning personnel {personnel_id}")
            # await self.receive_and_check_message(
            #    patient_ws, "patient-measurement-finished"
            # )
            await self.global_consume_message_type("resource-assignments")
            await self.finish_measurements(patient_ws)
            # _, other_ws = self.patient_queue[1]
            # await self.receive_and_check_message(
            #    other_ws, "patient-measurement-finished"
            # )

    async def assign_material(self):
        patient_code, patient_ws = self.patient_queue[0]
        await patient_ws.send(
            json.dumps(
                {"messageType": "material-assign", "materialId": self.material_id}
            )
        )
        await self.global_consume_message_type("resource-assignments")
        print("trying to finish measurements", flush=True)
        await self.finish_measurements(patient_ws)

    async def start_examination(self):
        patient_code, patient_ws = self.patient_queue[0]
        await patient_ws.send(
            json.dumps(
                {"messageType": "action-add", "actionName": "Blutzucker analysieren"}
            )
        )
        await self.receive_and_check_message(patient_ws, "action-confirmation")
        await self.receive_and_check_message(patient_ws, "action-list")
        await self.finish_measurements(patient_ws)


def process_message(data: json):
    data = json.loads(data)
    mt = data.get("messageType")
    print(mt)
    if mt == "failure":
        # TODO: Implement failure handling (e.g., show error toast)
        pass
    elif mt == "warning":
        # TODO: Implement warning handling (e.g., show warning toast)
        pass
    elif mt == "test-passthrough":
        # TODO: Implement test-passthrough handling (e.g., show warning toast)
        pass
    elif mt == "patient-measurement-finished":
        return "patient-measurement-finished"
    elif mt == "trainer-measurement-finished":
        return "trainer-measurement-finished"
    elif mt == "state":
        # TODO: Load state from data (e.g., update patientStore with state information)
        pass
    elif mt == "available-patients":
        # TODO: Load available patients and initialize patientStore accordingly
        pass
    elif mt == "available-actions":
        # TODO: Load available actions into the store
        pass
    elif mt == "exercise":
        print(data.get("exercise"))
        pass
    elif mt == "exercise-start":
        # TODO: Set exerciseStore status to 'running' and update screens (e.g., STATUS and ACTIONS)
        pass
    elif mt == "exercise-pause":
        # TODO: Set exerciseStore status to 'paused' and switch to waiting screen
        pass
    elif mt == "exercise-resume":
        # TODO: Set exerciseStore status to 'running' and update screens (e.g., STATUS and ACTIONS)
        pass
    elif mt == "exercise-end":
        # TODO: Set exerciseStore status to 'ended' and show ended screen
        pass
    elif mt == "delete":
        # TODO: Handle delete event
        pass
    elif mt == "information":
        # TODO: Handle information event
        pass
    elif mt == "action-confirmation":
        # TODO: Allow new actions as confirmation of prior action
        pass
    elif mt == "action-declination":
        # TODO: Allow new actions and show error toast for action declination
        pass
    elif mt == "action-result":
        # TODO: Handle action result event
        pass
    elif mt == "resource-assignments":
        # TODO: Set resource assignments in the corresponding store
        pass
    elif mt == "action-list":
        # TODO: Process action list and start updating timers as needed
        pass
    elif mt == "visible-injuries":
        # TODO: Load visible injuries into the store
        pass
    elif mt == "action-check":
        # TODO: Update action check store with provided data
        pass
    elif mt == "patient-relocating":
        # TODO: Update patientStore for relocating patient and set waiting screen
        pass
    elif mt == "patient-back":
        # TODO: Reset patientStore status after patient is back and update screens
        pass
    else:
        # TODO: Handle unknown message types (e.g., show error toast/log error)
        pass


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


async def start_exercise(
    trainer_ws: websockets.WebSocketClientProtocol,
    patients_ws: list[websockets.WebSocketClientProtocol],
):
    await trainer_ws.send(json.dumps({"messageType": "exercise-start"}))
    exercise_start = await trainer_ws.recv()
    for patient_ws in patients_ws:
        exercise_start = await patient_ws.recv()
        action_list = await patient_ws.recv()


async def ghost_consume(
    idle_ws: list[websockets.WebSocketClientProtocol], expected_type=None
):
    for ws in idle_ws:
        message = await ws.recv()
        message_type = json.loads(message).get("messageType")
        if expected_type and message_type != expected_type:
            raise ValueError(
                f"Expected message type {expected_type}, got {message_type}"
            )


async def main():
    # Login via HTTP to get tokens before WebSocket connections
    trainer_name = f"trainer_created_{datetime.datetime.now()}"
    print(trainer_name)
    trainer_token = login_trainer(trainer_name, "trainer_password")

    # Check if login was successful
    if not trainer_token:
        raise ConnectionRefusedError("Login failed for one or more clients; aborting")
    trainer_ws = await generate_trainer_websocket(trainer_token)
    patient_count = 2
    area_size = 2
    patient_ids, personnel_ids, material_ids, exercise_id = await setup_exercise(
        trainer_ws, patient_count, area_size
    )
    tokens = [login_patient(exercise_id, patient_id) for patient_id in patient_ids]
    patients_ws = await asyncio.gather(
        *[generate_patient_websocket(token) for token in tokens]
    )
    for i in range(len(material_ids)):
        i_1 = i // 2
        i_2 = (i // 2) + 1
        patient_group_instance = PatientGroup(
            ["1001", "1005"] * (patient_count // 2),
            [patients_ws[i_1], patients_ws[i_2]],
            trainer_ws,
            [personnel_ids[i_1], personnel_ids[i_2]],
            material_ids[i],
        )
        PatientGroup.register_for_simulation(patient_group_instance)
    await start_exercise(trainer_ws, patients_ws)
    try:
        await PatientGroup.execute_simulation()
    except Exception as e:
        print(e)
    finally:
        await trainer_ws.send(json.dumps({"messageType": "exercise-stop"}))
    idle_ws = patients_ws.copy()
    idle_ws.append(trainer_ws)

    for i, patient_ws in enumerate(patients_ws):
        idle_ws.pop(i)
        print("***********Next Patient***************", flush=True)
        await patient_ws.send(json.dumps({"messageType": "triage", "triage": 1}))
        await ghost_consume(idle_ws, "exercise")
        patient_is_processed = False

        while not patient_is_processed:
            message = await patient_ws.recv()
            patient_is_processed = (
                process_message(message) == "patient-measurement-finished"
            )
        print("Patient while loop completed", flush=True)

        trainer_is_processed = False
        while not trainer_is_processed:
            message = await trainer_ws.recv()
            trainer_is_processed = (
                process_message(message) == "trainer-measurement-finished"
            )
        print("Trainer while loop completed", flush=True)
        await patient_ws.send(json.dumps({"messageType": "triage", "triage": 2}))
        print("***********After second triage***************", flush=True)
        await ghost_consume(idle_ws, "exercise")
        message = await patient_ws.recv()
        process_message(message)
        patient_measurement_finished = await patient_ws.recv()
        process_message(patient_measurement_finished)
        trainer_measurement_finished = await trainer_ws.recv()
        idle_ws.insert(i, patient_ws)

    await trainer_ws.send(json.dumps({"messageType": "exercise-stop"}))


if __name__ == "__main__":
    asyncio.run(main())
