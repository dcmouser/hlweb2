# Generated by Django 5.0.3 on 2024-05-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0028_alter_game_gamename_alter_game_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="game",
            name="uuid",
        ),
        migrations.AddField(
            model_name="game",
            name="subdirname",
            field=models.CharField(
                blank=True,
                help_text="Subdirectory name for holding files",
                max_length=64,
            ),
        ),
    ]
