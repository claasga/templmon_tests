# Generated by Django 5.0.1 on 2024-10-12 16:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("template", "0010_merge_20240710_1548"),
    ]

    operations = [
        migrations.AlterField(
            model_name="patientstate",
            name="transition",
            field=models.ForeignKey(
                help_text="Should never be null except for during creation",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="template.statetransition",
            ),
        ),
    ]
