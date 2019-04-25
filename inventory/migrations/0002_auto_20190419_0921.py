# Generated by Django 2.1.5 on 2019-04-19 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SanitationRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('employee_name', models.CharField(max_length=25)),
                ('equipment_sanitized', models.CharField(max_length=100)),
                ('chemicals_used', models.CharField(max_length=100)),
                ('note', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='slot',
            name='barcode',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]