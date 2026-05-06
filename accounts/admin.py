from django.contrib import admin

from .models import CandidateProfile, JobApplication


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "user_type", "profile_completion", "email_verified", "phone_verified")
    search_fields = ("user__email", "user__first_name", "user__last_name", "phone", "skills")
    list_filter = ("user_type", "email_verified", "phone_verified", "hide_from_recruiters")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "status", "applied_at")
    search_fields = ("user__email", "job_title")
    list_filter = ("status",)
