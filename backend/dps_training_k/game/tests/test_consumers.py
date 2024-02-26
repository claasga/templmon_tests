from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from configuration.asgi import application
from game.models import User
from rest_framework.authtoken.models import Token


class TrainerConsumerTestCase(TransactionTestCase):
    maxDiff = None

    async def test_trainer_consumer_example_request(self):
        path = "/ws/trainer/"
        communicator = WebsocketCommunicator(application, path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send an "example" request type message to the server
        await communicator.send_json_to(
            {"messageType": "example", "exercise_code": "123"}
        )

        # Receive and test the response from the server
        response = await communicator.receive_json_from()
        self.assertEqual(
            response, {"messageType": "response", "content": "exercise_code 123"}
        )

        # Close the connection
        await communicator.disconnect()

    async def test_trainer_handle_create_exercise(self):
        path = "/ws/trainer/"
        communicator = WebsocketCommunicator(application, path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send an "example" request type message to the server
        await communicator.send_json_to({"messageType": "trainer-exercise-create"})

        # Receive and test the response from the server
        response = await communicator.receive_json_from()
        content = {
            "exerciseCode": "123456",
            "areas": [
                {
                    "name": "ZNA",
                    "patients": [
                        {
                            "name": "Max Mustermann",
                            "patientCode": 123456,
                            "patientId": 5,
                            "patientDatabaseId": 3,
                        }
                    ],
                    "personnel": [
                        {
                            "name": "Hanna Schulz",
                            "role": "Arzt",
                            "personnelDatabaseId": 6,
                        }
                    ],
                    "devices": [{"name": "EKG", "deviceDatabaseId": 15}],
                }
            ],
        }
        self.assertEqual(
            response, {"messageType": "trainer-exercise-create", "exercise": content}
        )

        # Close the connection
        await communicator.disconnect()

    async def test_trainer_consumer_test_passthrough_request(self):
        path = "/ws/trainer/"
        communicator = WebsocketCommunicator(application, path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send an "example" request type message to the server
        await communicator.send_json_to({"messageType": "test-passthrough"})

        # Receive and test the response from the server
        response = await communicator.receive_json_from()
        self.assertEqual(
            response,
            {"messageType": "test-passthrough", "message": "received test event"},
        )

        # Close the connection
        await communicator.disconnect()
