# Generated by Django 3.2.4 on 2021-07-04 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto_poster', '0004_auto_20210703_0636'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_republished',
            field=models.BooleanField(default=True),
        ),
    ]
