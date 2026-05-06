from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="profile_photo",
            field=models.FileField(blank=True, null=True, upload_to="profile_photos/"),
        ),
    ]
