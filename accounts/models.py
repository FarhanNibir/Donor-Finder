from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

BLOOD_GROUPS = [(g, g) for g in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]]
COOLDOWN_DAYS = 120  # about 4 months


class DonorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    phone = models.CharField(max_length=20)
    district = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_donated_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # donor can hide themselves

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.last_donated_at is None:
            return True
        return timezone.now().date() >= self.last_donated_at + timedelta(days=COOLDOWN_DAYS)

    @property
    def available_again_on(self):
        if self.last_donated_at is None:
            return None
        return self.last_donated_at + timedelta(days=COOLDOWN_DAYS)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.blood_group})"