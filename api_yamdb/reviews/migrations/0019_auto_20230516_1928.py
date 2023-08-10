# Generated by Django 3.2 on 2023-05-16 16:28

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0018_merge_20230515_2035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(validators=[reviews.validators.year_validator], verbose_name='Дата выхода'),
        ),
    ]
