# Generated by Django 3.2.8 on 2021-11-07 09:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_user_is_moderator"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_reporter",
            field=models.BooleanField(default=False),
        ),
    ]
