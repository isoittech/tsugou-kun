# Generated by Django 2.2 on 2020-08-24 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_sankasha_anshou_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='anshou_num',
        ),
        migrations.RemoveField(
            model_name='sankasha',
            name='anshou_num',
        ),
    ]
