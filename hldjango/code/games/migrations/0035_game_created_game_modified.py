# Generated by Django 5.0.3 on 2024-06-29 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0034_alter_game_buildresultsjsonfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="game",
            name="modified",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]