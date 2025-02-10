from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "game"

    def ready(self):
        import os

        process_id = int(os.environ.get("PROCESS_ID", "0"))
        # Only register listener if this is the django process (PROCESS_ID equals 0)
        if process_id != 0:
            return

        # Import and register the listener function
        from .channel_notifications import redis_publish_obj
        from .redis_comm import start_listener_in_thread

        start_listener_in_thread(redis_publish_obj)
        print("Django listener thread started.")
