# Generated by Django 5.0.3 on 2024-11-11 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0037_game_instructions"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="status",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Status (parsed from game text)",
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="game",
            name="instructions",
            field=models.TextField(
                blank=True,
                default="",
                help_text="List of additional instructions and downloads needed to play, in Markdown format.",
                verbose_name="Additional requirements and instructions (markdown)",
            ),
        ),
    ]
