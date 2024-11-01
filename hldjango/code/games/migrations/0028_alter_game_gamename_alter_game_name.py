# Generated by Django 5.0.3 on 2024-05-29 06:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0027_alter_game_gamename_alter_game_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="gameName",
            field=models.CharField(
                blank=True, default="", help_text="Public name of game", max_length=80
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="name",
            field=models.CharField(
                help_text="Internal name of the game",
                max_length=50,
                validators=[django.core.validators.RegexValidator("^[\\w]+$")],
                verbose_name="Short name",
            ),
        ),
    ]
