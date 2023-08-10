# Generated by Django 3.2 on 2023-05-08 22:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(
                default='sad@gmail.com', max_length=254, unique=True
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, 'user'), (2, 'admin'), (3, 'moderator')],
                default=1,
                null=True,
            ),
        ),
    ]
