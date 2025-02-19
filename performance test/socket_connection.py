import asyncio
import json
import requests
import websockets

# REST endpoint URLs for login views
TRAINER_LOGIN_URL = "http://localhost:8000/api/trainer/login"
PATIENT_LOGIN_URL = "http://localhost:8000/api/patient/login"

# WebSocket endpoint URLs
TRAINER_WS_URI = "ws://localhost:8000/ws/trainer"
PATIENT_WS_URI = "ws://localhost:8000/ws/patient"


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


async def trainer_consumer(token):
    # Include the token in an authentication message
    async with websockets.connect(TRAINER_WS_URI + "/?token=" + token) as websocket:
        print("Websocket connection built")

        response = await websocket.recv()
        print("Trainer response:", response)
        await websocket.send(json.dumps({"messageType": "test-passthrough"}))
        response = await websocket.recv()
        print("Trainer response:", response)


async def patient_consumer(token):
    async with websockets.connect(PATIENT_WS_URI + "/?token=" + token) as websocket:
        auth_payload = json.dumps({"type": "authenticate", "token": token})
        await websocket.send(auth_payload)
        print("Patient: Authentication message sent")

        response = await websocket.recv()
        print("Patient response:", response)


async def main():
    # Login via HTTP to get tokens before WebSocket connections
    trainer_token = login_trainer("trainer_username", "trainer_password")

    # Check if login was successful
    if not trainer_token:
        raise ConnectionRefusedError("Login failed for one or more clients; aborting")

    # Start WebSocket consumers with the respective tokens
    await trainer_consumer(trainer_token)


if __name__ == "__main__":
    asyncio.run(main())
