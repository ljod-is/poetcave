# Generated by Django 3.2.5 on 2021-07-10 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poem', '0014_auto_20210308_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poem',
            name='editorial_status',
            field=models.CharField(choices=[('pending', 'Í bið'), ('approved', 'Samþykkt'), ('rejected', 'Hafnað')], default='pending', max_length=20),
        ),
    ]