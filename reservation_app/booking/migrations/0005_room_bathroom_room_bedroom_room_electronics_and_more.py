# Generated by Django 5.2.1 on 2025-06-06 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_remove_hotel_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='bathroom',
            field=models.TextField(default='Ванная комната'),
        ),
        migrations.AddField(
            model_name='room',
            name='bedroom',
            field=models.TextField(default='Односпальная кровать'),
        ),
        migrations.AddField(
            model_name='room',
            name='electronics',
            field=models.TextField(default='Холодильник, телевизор'),
        ),
        migrations.AddField(
            model_name='room',
            name='internet',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='room',
            name='nutrition',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='room',
            name='square',
            field=models.PositiveIntegerField(default=20),
            preserve_default=False,
        ),
    ]
