# Generated by Django 3.1.5 on 2021-02-13 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]