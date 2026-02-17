"""
WSGI config for garden_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

# Monkeypatch django.dispatch.Signal to avoid TypeError with dmqtt on Django 4.0+
import django.dispatch

original_signal_init = django.dispatch.Signal.__init__


def patched_signal_init(self, providing_args=None, use_caching=False):  # noqa: ARG001
    original_signal_init(self, use_caching=use_caching)


django.dispatch.Signal.__init__ = patched_signal_init

from django.core.wsgi import get_wsgi_application  # noqa: E402

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "garden_api.settings")

application = get_wsgi_application()
