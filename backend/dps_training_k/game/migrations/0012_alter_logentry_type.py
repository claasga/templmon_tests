# Generated by Django 5.0.1 on 2025-02-06 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_delete_logrulefile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='type',
            field=models.CharField(blank=True, choices=[('AR', 'arrived'), ('AS', 'assigned'), ('UA', 'unassigned'), ('ST', 'started'), ('FI', 'finished'), ('CA', 'canceled'), ('IE', 'in effect'), ('EX', 'expired'), ('MO', 'moved'), ('TR', 'triaged'), ('UP', 'updated')], max_length=2, null=True),
        ),
    ]
