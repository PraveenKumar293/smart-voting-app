# users/models.py
from django.contrib.auth.models import AbstractUser     #Import Django’s base user class so we can extend it.
from django.db import models   #Import Django ORM model base.
from django.utils import timezone  #Time utilities (timezone-aware timestamps).

class CustomUser(AbstractUser):  #Define a new user model that inherits Django’s AbstractUser (keeps username/password/auth features).
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    aadhaar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    voter_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    has_voted = models.BooleanField(default=False)  #Store voter id. Unique per voter.
    is_area_admin = models.BooleanField(default=False)
    face_encoding = models.TextField(null=True, blank=True)  # JSON/text store for face vector

    def age(self):
        if not self.dob:
            return None
        from datetime import date
        today = date.today()
        # calculate full years
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, default='login')  # 'login' or 'vote' etc.
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.used) and (timezone.now() <= self.expires_at)
