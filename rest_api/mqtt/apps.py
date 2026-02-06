from django.apps import AppConfig

class MqttConfig(AppConfig):
    name = 'mqtt'

    def ready(self):
        # Import signals when the app is ready
        import sys
        if 'runserver' in sys.argv or 'mqtt' in sys.argv:
            from . import connection, data, subscriptions
