# Generated by Django 2.1.5 on 2019-10-10 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20191009_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
