from cerberus import Validator

DATA_SCHEMA = {
    "dataId": {"type": "string", "required": True},
    "frequency": {"type": "float", "required": True},
    "value": {"type": "float", "required": True},
    "type": {"type": "string", "required": True},
    "serial_machine": {"type": "string", "required": True},
    "machineId": {"type": "string", "required": True},
    "channelId": {"type": "string", "required": True},
}


class DataValidator:
    def __init__(self):
        self.validator = Validator(DATA_SCHEMA)

    def validate(self, data):
        if not self.validator.validate(data):
            return False, self.validator.errors
        return True, None
