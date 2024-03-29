# Generated by Django 3.1.5 on 2021-02-14 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("poem", "0007_auto_20210214_0317"),
    ]

    operations = [
        migrations.AddField(
            model_name="poem",
            name="date_created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="poem",
            name="date_updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="poem",
            name="trashed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="poem",
            name="trashed_timing",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="poem",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="poems",
                to="poem.author",
            ),
        ),
        migrations.AlterField(
            model_name="poem",
            name="name",
            field=models.CharField(max_length=150),
        ),
    ]
