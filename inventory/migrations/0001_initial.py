# Generated by Django 2.1.5 on 2019-03-03 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tray_size', models.CharField(choices=[('1020', 'Standard - 10" × 20"'), ('1010', '10" × 10"'), ('0505', '5" × 5"')], default='1020', max_length=4)),
                ('live_delivery', models.BooleanField(default=True)),
                ('exp_num_germ_days', models.IntegerField()),
                ('exp_num_grow_days', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CropRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('record_type', models.CharField(choices=[('SEED', 'Seeded'), ('GERM', 'Germinated/Sprouted'), ('GROW', 'Growth Milestone'), ('WATER', 'Watered'), ('HARVEST', 'Harvested'), ('DELIVERED', 'Delivered to Customer'), ('TRASH', 'Disposed'), ('RETURNED', 'Tray Returned'), ('NOTE', 'Notes')], max_length=10)),
                ('note', models.CharField(max_length=200)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('current_crop', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='Variety',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('days_plant_to_harvest', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='crop',
            name='variety',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Variety'),
        ),
    ]
