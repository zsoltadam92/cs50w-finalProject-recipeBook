# Generated by Django 4.2.9 on 2024-04-14 20:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0006_recipe_categories_alter_recipe_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='rating',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AddField(
            model_name='recipe',
            name='rating_count',
            field=models.IntegerField(default=0),
        ),
    ]
