# Generated by Django 4.2.9 on 2024-04-15 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0007_recipe_rating_recipe_rating_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='rating_count',
        ),
        migrations.AddField(
            model_name='recipe',
            name='average_rating',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ratings',
            field=models.JSONField(default=dict),
        ),
    ]