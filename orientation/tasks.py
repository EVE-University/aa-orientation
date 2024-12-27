"""Tasks."""
from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now
from orientation.models import NewMembers
from orientation.app_settings import ORIENTATIONDAYS

import logging


logger = logging.getLogger(__name__)

@shared_task
def delete_old_members():
    """Delete NewMembers entries older than X days."""
    threshold_date = now() - timedelta(days=ORIENTATIONDAYS)
    old_entries = NewMembers.objects.filter(created_date__lt=threshold_date)

    count = old_entries.count()
    if count > 0:
        old_entries.delete()
        logger.debug(f"Deleted {count} NewMembers entries older than {ORIENTATIONDAYS} days.")
    else:
        logger.debug("No old NewMembers entries to delete.")