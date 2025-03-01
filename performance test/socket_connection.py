import asyncio
import json
import requests
import websockets
import random
import datetime

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
    exercise = json.loads(exercise_json).get("exercise")
    print(exercise)
    areas = exercise.get("areas")
    for area in areas:
        patient_ids.extend(
            [patient.get("patientId") for patient in area.get("patients")]
        )
    print(patient_ids)
    return patient_ids, exercise.get("exerciseId")


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
    patient_ids, exercise_id = await setup_exercise(trainer_ws, 2, 2)
    tokens = [login_patient(exercise_id, patient_id) for patient_id in patient_ids]
    patients_ws = await asyncio.gather(
        *[generate_patient_websocket(token) for token in tokens]
    )
    idle_ws = patients_ws.copy()
    idle_ws.append(trainer_ws)
    await start_exercise(trainer_ws, patients_ws)
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
        trainer_measurement_finished = await trainer_ws.recv()
        idle_ws.insert(i, patient_ws)

    await trainer_ws.send(json.dumps({"messageType": "exercise-stop"}))


if __name__ == "__main__":
    asyncio.run(main())
