"""Models."""

from django.db import models

from allianceauth.hrapplications.models import Application

class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)

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
