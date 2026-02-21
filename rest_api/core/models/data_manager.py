import logging
import uuid
from datetime import datetime, timezone
from django.conf import settings
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class DataBucketManager:
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        # Always fetch fresh db name from settings to support django's test db switching
        from django.db import connection
        db_name = settings.DATABASES['default']['NAME']
        if cls._db is None or cls._client.address == None:
             cls._client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        
        return cls._client[db_name]

    @classmethod
    def add_reading(cls, machine, channel, data_type, value, timestamp, frequency, serial_machine):
        """
        Adds a single sensor reading to an hourly bucket.
        Creates the bucket if it doesn't exist.
        """
        db = cls.get_db()
        collection = db['core_data']

        # Ensure timestamp is datetime
        if isinstance(timestamp, str):
            try:
                # Assuming ISO format from payload
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                dt = datetime.now(timezone.utc)
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            dt = timestamp or datetime.now(timezone.utc)

        # Calculate base_date (beginning of the hour)
        base_date = dt.replace(minute=0, second=0, microsecond=0)

        machine_id = machine.machineId if machine else None
        channel_id = channel.idChannel if channel else None

        query = {
            "machineId_id": machine_id,
            "channelId_id": channel_id,
            "base_date": base_date,
            "type": data_type,
            "frequency": str(frequency)
        }

        # The reading to push
        reading = {
            "v": float(value),
            "t": dt.isoformat(),
            "f": str(frequency)
        }

        update = {
            "$push": {"readings": reading},
            "$inc": {"count": 1},
            "$setOnInsert": {
                "idData": str(uuid.uuid4()),
                "createAt": datetime.now(timezone.utc),
                "serial_machine": serial_machine,
                "frequency": str(frequency)
            }
        }

        try:
            result = collection.update_one(query, update, upsert=True)
            return result
        except Exception as e:
            logger.error(f"Error adding reading to bucket: {e}")
            raise
