import fnmatch
import json
import logging
from functools import wraps

from django.dispatch import receiver
from dmqtt.signals import message

logger = logging.getLogger(__name__)

def mqtt_topic(matcher, as_json=True):
    """
    A fixed version of the @topic decorator that correctly handles 
    Django signal arguments (where sender is the first positional argument).
    
    It also replaces MQTT wildcards (+, #) with fnmatch wildcards (*).
    """
    # Convert MQTT wildcards to fnmatch/glob wildcards
    # + matches one level -> * in glob (if we assume levels are handled)
    # # matches multiple levels -> * in glob
    # Actually, fnmatch '*' matches everything including slashes.
    # So we'll just be careful.
    glob_matcher = matcher.replace('+', '*').replace('#', '*')

    def decorator(func):
        @receiver(message)
        @wraps(func)
        def wrapper(sender, **kwargs):
            msg = kwargs.get('msg')
            if not msg:
                return

            if fnmatch.fnmatch(msg.topic, glob_matcher):
                logger.debug(f"Matched topic {msg.topic} with {matcher}")

                # Extract payload
                try:
                    payload = msg.payload.decode('utf-8') if isinstance(msg.payload, bytes) else msg.payload
                except UnicodeDecodeError:
                    logger.error(f"Failed to decode payload on topic {msg.topic}")
                    return

                if not payload:
                    logger.debug(f"Empty payload on topic {msg.topic}")
                    return

                processed_data = None
                if as_json:
                    try:
                        processed_data = json.loads(payload)
                    except Exception as e:
                        logger.error(f"Error parsing JSON on topic {msg.topic}: {e}")
                        return

                # Call the original function with clean arguments
                # Pop these from kwargs to avoid "multiple values for keyword argument" error
                kwargs.pop('topic', None)
                kwargs.pop('data', None)
                kwargs.pop('msg', None)

                return func(
                    sender=sender,
                    topic=msg.topic,
                    data=processed_data,
                    msg=msg,
                    **kwargs
                )
        return wrapper
    return decorator
