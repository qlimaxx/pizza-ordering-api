# Generated by Django 2.2.5 on 2019-09-20 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-created_at',)},
        ),
    ]
