from django.apps import AppConfig


class MqttConfig(AppConfig):
    name = "mqtt"

    def ready(self):
        # Import signals when the app is ready
        import sys

        # Note: 'mqtt' might be used if you have a custom management command or similar
        if "runserver" in sys.argv or "mqtt" in sys.argv:
            self._launch_mqtt()

    def _launch_mqtt(self):
        # Import handlers locally to ensure all models are already loaded
        import logging

        from . import connection, data, subscriptions  # noqa: F401

        logger = logging.getLogger(__name__)
        logger.info("MQTT handlers (connection, data, subscriptions) successfully launched.")
