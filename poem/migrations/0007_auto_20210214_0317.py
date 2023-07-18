# Generated by Django 3.1.5 on 2021-02-14 03:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("poem", "0006_author_user"),
    ]

    operations = [
        migrations.RenameField(
            model_name="poem",
            old_name="description",
            new_name="about",
        ),
        migrations.RenameField(
            model_name="poem",
            old_name="approved_by",
            new_name="editorial_user",
        ),
        migrations.RemoveField(
            model_name="poem",
            name="approved",
        ),
        migrations.RemoveField(
            model_name="poem",
            name="approved_timing",
        ),
        migrations.AddField(
            model_name="poem",
            name="editorial_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="poem",
            name="editorial_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Samþykkt"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="poem",
            name="editorial_timing",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="poem",
            name="public_timing",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
