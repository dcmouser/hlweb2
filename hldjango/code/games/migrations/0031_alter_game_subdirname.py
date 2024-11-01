# Generated by Django 5.0.3 on 2024-05-29 16:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0030_alter_game_subdirname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="subdirname",
            field=models.CharField(
                default=uuid.uuid4,
                help_text="Subdirectory name for holding files",
                max_length=64,
                unique=True,
            ),
        ),
    ]
