# Generated by Django 5.2.1 on 2025-05-15 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SpotyRate', '0003_spotifyuser_groups_spotifyuser_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spotifyuser',
            name='profile_image_url',
        ),
    ]
