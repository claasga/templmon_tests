# Generated by Django 5.0.1 on 2024-05-23 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('template', '0019_rename_data_patientstate_vital_signs_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientstate',
            name='special_events',
            field=models.CharField(blank=True, help_text='Perceivable events of high priority, e.g. "Patient schreit vor Schmerzen"', null=True),
        ),
    ]
