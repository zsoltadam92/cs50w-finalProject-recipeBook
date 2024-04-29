# Generated by Django 4.2.9 on 2024-04-28 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recepies', '0018_ingredient_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='comments_on_recipe', to='recepies.comment'),
        ),
    ]