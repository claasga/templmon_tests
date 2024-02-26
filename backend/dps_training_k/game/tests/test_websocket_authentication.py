from django.test import TransactionTestCase
from game.models import User
from rest_framework.authtoken.models import Token
from configuration.asgi import application
from channels.testing import WebsocketCommunicator


class PatientWebSocketTest(TransactionTestCase):
    def setUp(self):
        super().setUp()
        # Create a user and token for testing
        self.user = User.objects.create_user(username="testpatient123", password="test")
        self.token, _ = Token.objects.get_or_create(user=self.user)

    async def test_authenticated_websocket_connection(self):
        # Connect to the WebSocket
        communicator = WebsocketCommunicator(
            application=application, path=f"/ws/patient/?token={self.token.key}"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected, "Failed to connect to WebSocket")

        # Send a message to the WebSocket
        await communicator.send_json_to(
            {
                "messageType": "example",
                "exercise_code": "exercise123",
                "patient_code": "patient123",
            }
        )

        # Receive the response from the WebSocket
        response = await communicator.receive_json_from()
        self.assertEqual(
            response,
            {
                "messageType": "response",
                "content": "exercise_code exercise123 & patient_code patient123",
            },
            "Unexpected response from WebSocket",
        )

        # Clean up
        await communicator.disconnect()
