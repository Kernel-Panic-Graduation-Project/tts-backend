# Generated by Django 5.2 on 2025-04-25 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audio_processor", "0007_alter_audiofile_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="audiofile",
            name="duration",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="audiofile",
            name="user_id",
            field=models.IntegerField(default=0),
        ),
    ]
