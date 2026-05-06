from django.conf import settings
from django.db import models
from django.utils import timezone


class CandidateProfile(models.Model):
    FRESHER = "fresher"
    EXPERIENCED = "experienced"
    USER_TYPE_CHOICES = [
        (FRESHER, "Fresher"),
        (EXPERIENCED, "Experienced"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=FRESHER)
    profile_photo = models.FileField(upload_to="profile_photos/", blank=True, null=True)
    disability = models.CharField(max_length=80, blank=True)
    current_location = models.CharField(max_length=120, blank=True)
    preferred_location = models.CharField(max_length=120, blank=True)
    education = models.TextField(blank=True)
    employment_history = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    salary_expectation = models.CharField(max_length=80, blank=True)
    notice_period = models.CharField(max_length=80, blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    resume_keywords = models.TextField(blank=True)
    profile_code = models.CharField(max_length=20, unique=True, blank=True)
    profile_completion = models.PositiveSmallIntegerField(default=0)
    profile_views = models.PositiveIntegerField(default=0)
    freshness_score = models.PositiveSmallIntegerField(default=0)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    hide_from_recruiters = models.BooleanField(default=False)
    blocked_companies = models.TextField(blank=True)
    communication_settings = models.TextField(blank=True)
    last_active_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.profile_code and self.user.email:
            seed = abs(hash(self.user.email)) % 36**8
            self.profile_code = f"AJ-{base36(seed).upper().zfill(8)[:8]}"
        self.profile_completion = self.calculate_completion()
        super().save(*args, **kwargs)

    @property
    def is_searchable(self):
        return self.email_verified and self.phone_verified and not self.hide_from_recruiters

    def mark_active(self):
        self.last_active_at = timezone.now()
        self.freshness_score = 100
        self.save(update_fields=["last_active_at", "freshness_score", "profile_completion", "updated_at"])

    def calculate_completion(self):
        weighted_fields = [
            (self.user.get_full_name(), 10),
            (self.user.email, 10),
            (self.phone, 10),
            (self.email_verified and self.phone_verified, 10),
            (self.current_location, 8),
            (self.preferred_location, 8),
            (self.education, 10),
            (self.skills, 12),
            (self.profile_photo, 8),
            (self.resume or self.resume_keywords, 10),
            (self.employment_history if self.user_type == self.EXPERIENCED else True, 4),
        ]
        return min(100, sum(weight for value, weight in weighted_fields if value))

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} ({self.profile_code})"


class JobApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=160)
    status = models.CharField(max_length=40, default="Pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.user.email} - {self.job_title}"


def base36(number):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number == 0:
        return "0"
    digits = []
    while number:
        number, remainder = divmod(number, 36)
        digits.append(alphabet[remainder])
    return "".join(reversed(digits))
