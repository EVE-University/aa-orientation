"""Admin site."""

from django.contrib import admin

# Register your models for the admin site here.

from . import models

admin.site.register(models.NewMembers)