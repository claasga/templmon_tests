# Generated by Django 5.0.1 on 2024-06-28 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("template", "0007_material_is_lab_alter_material_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="patientinformation",
            name="pretreatment_action_templates",
            field=models.JSONField(default=list),
        ),
    ]
