# Generated by Django 5.0.2 on 2024-03-29 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='processing_info',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
