# Generated by Django 5.0.1 on 2024-05-08 08:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0038_actioninstance_lab'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lab',
            name='name',
        ),
        migrations.AlterField(
            model_name='actioninstance',
            name='area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.area'),
        ),
    ]
