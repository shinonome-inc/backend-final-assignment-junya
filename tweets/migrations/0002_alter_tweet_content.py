# Generated by Django 4.1.3 on 2023-03-14 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='content',
            field=models.TextField(max_length=100),
        ),
    ]
