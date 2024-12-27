"""App settings."""

from django.conf import settings

ORIENTATIONDAYS = getattr(settings, "ORIENTATIONDAYS", 31)
