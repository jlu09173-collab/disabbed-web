from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(max_length=20, unique=True)),
                ("user_type", models.CharField(choices=[("fresher", "Fresher"), ("experienced", "Experienced")], default="fresher", max_length=20)),
                ("disability", models.CharField(blank=True, max_length=80)),
                ("current_location", models.CharField(blank=True, max_length=120)),
                ("preferred_location", models.CharField(blank=True, max_length=120)),
                ("education", models.TextField(blank=True)),
                ("employment_history", models.TextField(blank=True)),
                ("skills", models.TextField(blank=True)),
                ("salary_expectation", models.CharField(blank=True, max_length=80)),
                ("notice_period", models.CharField(blank=True, max_length=80)),
                ("resume", models.FileField(blank=True, null=True, upload_to="resumes/")),
                ("resume_keywords", models.TextField(blank=True)),
                ("profile_code", models.CharField(blank=True, max_length=20, unique=True)),
                ("profile_completion", models.PositiveSmallIntegerField(default=0)),
                ("profile_views", models.PositiveIntegerField(default=0)),
                ("freshness_score", models.PositiveSmallIntegerField(default=0)),
                ("email_verified", models.BooleanField(default=False)),
                ("phone_verified", models.BooleanField(default=False)),
                ("hide_from_recruiters", models.BooleanField(default=False)),
                ("blocked_companies", models.TextField(blank=True)),
                ("communication_settings", models.TextField(blank=True)),
                ("last_active_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_title", models.CharField(max_length=160)),
                ("status", models.CharField(default="Pending", max_length=40)),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-applied_at"]},
        ),
    ]
