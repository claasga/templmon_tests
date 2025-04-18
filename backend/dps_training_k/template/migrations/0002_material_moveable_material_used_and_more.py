# Generated by Django 5.0.1 on 2024-05-31 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('template', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='moveable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='material',
            name='used',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='material',
            name='category',
            field=models.CharField(choices=[('DE', 'Device'), ('BL', 'Blood'), ('LA', 'Labor')], max_length=2),
        ),
    ]
