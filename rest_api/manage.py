#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

# Monkeypatch django.dispatch.Signal to avoid TypeError with dmqtt on Django 4.0+
# dmqtt uses providing_args which was removed in Django 4.0
import django.dispatch

original_signal_init = django.dispatch.Signal.__init__


def patched_signal_init(self, providing_args=None, use_caching=False):  # noqa: ARG001
    original_signal_init(self, use_caching=use_caching)


django.dispatch.Signal.__init__ = patched_signal_init


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "garden_api.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
