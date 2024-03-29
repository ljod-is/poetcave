# Generated by Django 3.2.9 on 2021-11-16 14:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("poem", "0021_alter_daypoem_day"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="author",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
