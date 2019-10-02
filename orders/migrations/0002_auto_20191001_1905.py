# Generated by Django 2.1.5 on 2019-10-01 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MicrogreenSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='harvestedcropproduct',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.MicrogreenSize'),
        ),
        migrations.AlterField(
            model_name='livecropproduct',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.MicrogreenSize'),
        ),
    ]