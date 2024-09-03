# Generated by Django 5.1 on 2024-09-03 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0007_alter_player_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='levelprize',
            name='received',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='prizes',
            field=models.ManyToManyField(blank=True, to='player.prize'),
        ),
    ]
