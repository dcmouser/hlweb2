# Generated by Django 5.0.3 on 2024-04-27 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0011_game_buildstats"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="buildStats",
            field=models.CharField(
                help_text="Computed build statistics",
                max_length=255,
                verbose_name="Build statistics",
            ),
        ),
    ]