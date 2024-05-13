# Generated by Django 5.0.1 on 2024-05-13 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0044_logentry_lab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='is_dirty',
            field=models.BooleanField(default=False, help_text='Set to True if objects is missing relevant Keys (e.g. timestamp)'),
        ),
    ]
