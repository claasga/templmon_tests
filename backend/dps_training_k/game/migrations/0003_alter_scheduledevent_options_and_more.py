# Generated by Django 5.0.1 on 2024-03-21 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_savedexercise_time_speed_up_owner_scheduledevent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledevent',
            options={'ordering': ['exercise', 'end_date']},
        ),
        migrations.RenameField(
            model_name='scheduledevent',
            old_name='date',
            new_name='end_date',
        ),
    ]
