# Generated by Django 5.0.1 on 2024-03-18 13:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedexercise',
            name='time_speed_up',
            field=models.FloatField(default=1.0),
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_events', to='game.exercise')),
                ('patient_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_events', to='game.patient')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('method_name', models.CharField(max_length=100)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='game.exercise')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='game.owner')),
            ],
            options={
                'ordering': ['exercise', 'date'],
            },
        ),
    ]
