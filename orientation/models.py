"""Models."""

from django.db import models

from allianceauth.authentication.models import State
from allianceauth.hrapplications.models import Application


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class OrientationAppConfig(models.Model):

    member_state = models.OneToOneField(
        State, on_delete=models.SET_NULL, null=True, blank=True, unique=True
    )

    def __str__(self):
        configs = []

        if self.member_state:
            configs.append(f"Member State: {self.member_state}")

        # Return a concatenated string of all active configurations
        return ", ".join(configs) if configs else "No Configuration Set"

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configuration"


class NewMembers(models.Model):
    """A model for registering when members are talked to"""

    class MembershipStates(models.IntegerChoices):
        NOTTALKED = 0, "Not Talked To"
        TALKED = 1, "Talked To"

    member_app = models.OneToOneField(
        Application, on_delete=models.CASCADE, null=True, blank=True
    )

    member_talked_state = models.IntegerField(
        choices=MembershipStates.choices, default=MembershipStates.NOTTALKED
    )

    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.member_app and self.member_app.user:
            return self.member_app.user.username
        return "No Application"

    class Meta:
        ordering = ["member_app__user__username"]
        verbose_name_plural = "New Members"

    @classmethod
    def all_new_members_in_corp(cls):
        """Return all new members who are in the corp only"""
        # Retrieve the current app configuration
        app_config = OrientationAppConfig.objects.first()
        if not app_config or not app_config.member_state:
            return (
                cls.objects.none()
            )  # Return an empty queryset if the config is incomplete

        return cls.objects.filter(
            member_app__user__profile__state=app_config.member_state
        ).order_by("member_talked_state", "created_date")
