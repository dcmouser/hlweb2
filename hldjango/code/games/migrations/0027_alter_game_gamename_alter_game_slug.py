# Generated by Django 5.0.3 on 2024-05-29 06:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0026_alter_game_slug_alter_game_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="gameName",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Public name of game",
                max_length=80,
                validators=[django.core.validators.RegexValidator("^[\\w]+$")],
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Unique slug id of the game",
                max_length=128,
                unique=True,
            ),
        ),
    ]
