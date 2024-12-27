
# **EVE Uni Orientation Plugin for Alliance Auth**

This is a plugin app for Alliance Auth designed to assist with member orientation and onboarding within EVE University.

---

## **Installation**

1. Add the app to your `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS += [
       'orientation',
   ]
   ```

2. Run the following commands to apply migrations and collect static files:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

---

## **Configuration**

You can set the number of days before old `NewMembers` entries are deleted by adding the following to your `settings.py`:
```python
ORIENTATIONDAYS = getattr(settings, "ORIENTATIONDAYS", 31)
```

By default, this is set to **31 days**.

---

## **Celery Schedule**

To enable automatic cleanup of old member entries, add the following task to your Celery schedule:

```python
CELERYBEAT_SCHEDULE["delete_old_members_daily"] = {
    "task": "orientation.tasks.delete_old_members",
    "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight
}
```

This task will remove `NewMembers` entries older than 31 days.
