# Generated by Django 5.0.3 on 2024-10-24 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0035_game_created_game_modified"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="extraCredits",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Extra credits (parsed from game text)",
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="extraInfo",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Extra information (parsed from game text)",
            ),
        ),
    ]