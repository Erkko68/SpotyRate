# Generated by Django 5.1.6 on 2025-02-17 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(max_length=255)),
            ],
        ),
    ]
