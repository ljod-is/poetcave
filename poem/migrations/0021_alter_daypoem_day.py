# Generated by Django 3.2.8 on 2021-11-03 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poem', '0020_author_private_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daypoem',
            name='day',
            field=models.DateField(blank=True),
        ),
    ]
