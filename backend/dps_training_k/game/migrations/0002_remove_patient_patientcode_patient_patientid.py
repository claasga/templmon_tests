# Generated by Django 5.0.1 on 2024-03-19 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='patientCode',
        ),
        migrations.AddField(
            model_name='patient',
            name='patientId',
            field=models.IntegerField(default=0, help_text='patientId used to log into patient - therefore part of authentication'),
            preserve_default=False,
        ),
    ]
