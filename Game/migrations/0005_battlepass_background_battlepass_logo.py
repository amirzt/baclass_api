# Generated by Django 5.1.2 on 2024-11-07 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0004_alter_avatarownership_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='battlepass',
            name='background',
            field=models.ImageField(default=None, null=True, upload_to='BattlePass/'),
        ),
        migrations.AddField(
            model_name='battlepass',
            name='logo',
            field=models.ImageField(default=None, null=True, upload_to='BattlePass/'),
        ),
    ]
