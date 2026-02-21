import json
from django.db import models

class SafeJSONField(models.JSONField):
    """
    Custom JSONField to handle Djongo's behavior where it sometimes returns 
    already-parsed lists/dicts from MongoDB, which causes Django's default 
    JSONField (which expects a string) to crash when trying to json.loads() it.
    """
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # If it's already a list or dict, don't try to parse it
        if isinstance(value, (list, dict)):
            return value
        return super().from_db_value(value, expression, connection)

    def db_type(self, connection):
        return 'json'
