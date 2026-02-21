from datetime import datetime

from cerberus import Validator


def to_datetime(value):
    """Coerce string to datetime if possible."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    return value


# Cerberus schema for machine data
DATA_SCHEMA = {
    "date_of_capture": {"type": "datetime", "required": True, "coerce": to_datetime},
    "frequency": {"type": "string", "required": True},
    "value": {"type": "float", "required": True},
    "type": {"type": "string", "required": True},
    "serial_machine": {"type": "string", "required": True},
}

# Schema for handle_machine_data input (kwargs)
MQTT_INPUT_SCHEMA = {
    "topic": {"type": "string", "required": True},
    "data": {
        "type": "list",
        "required": True,
        "minlength": 0,
        "schema": {"type": "dict", "schema": DATA_SCHEMA},
    },
}

data_validator = Validator(DATA_SCHEMA)
mqtt_input_validator = Validator(MQTT_INPUT_SCHEMA, allow_unknown=True)
