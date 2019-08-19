# Generated by Django 2.1.5 on 2019-07-24 15:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20190425_1233'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='CropAttribute',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=50)),
        #     ],
        # ),
        # migrations.CreateModel(
        #     name='CropAttributeOption',
        #     fields=[
        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('name', models.CharField(max_length=50)),
        #         ('attribute_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='inventory.CropAttribute')),
        #     ],
        # ),
        migrations.CreateModel(
            name='InHouse',
            fields=[
                ('variety', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='inventory.Variety')),
                ('num_small', models.IntegerField(default=0)),
                ('num_medium', models.IntegerField(default=0)),
                ('num_big', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='InventoryAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('action_type', models.CharField(choices=[('SEED', 'Seeded'), ('HARVEST', 'Harvested'), ('KILL', 'Killed')], max_length=10)),
                ('data', models.CharField(max_length=1000, null=True)),
                ('note', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeekdayRequirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plant_day', models.CharField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], max_length=1)),
                ('num_small', models.IntegerField(default=0)),
                ('num_medium', models.IntegerField(default=0)),
                ('num_big', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='crop',
            name='exp_num_germ_days',
        ),
        migrations.RemoveField(
            model_name='crop',
            name='exp_num_grow_days',
        ),
        migrations.RemoveField(
            model_name='crop',
            name='live_delivery',
        ),
        migrations.RemoveField(
            model_name='crop',
            name='tray_size',
        ),
        migrations.RemoveField(
            model_name='croprecord',
            name='note',
        ),
        migrations.RemoveField(
            model_name='variety',
            name='days_germ',
        ),
        migrations.RemoveField(
            model_name='variety',
            name='days_grow',
        ),
        migrations.AddField(
            model_name='crop',
            name='crop_yield',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crop',
            name='germ_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crop',
            name='grow_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crop',
            name='harvest_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crop',
            name='leaf_wingspan',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='crop',
            name='notes',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='croprecord',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='croprecord',
            name='record_type',
            field=models.CharField(choices=[('GERM', 'Started Germination Phase'), ('GROW', 'Started Grow Phase'), ('WATER', 'Watered'), ('HARVEST', 'Harvested'), ('TRASH', 'Trashed')], max_length=10),
        ),
        migrations.AlterField(
            model_name='sanitationrecord',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='slot',
            name='current_crop',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='current_slot', to='inventory.Crop'),
        ),
        migrations.AddField(
            model_name='weekdayrequirement',
            name='variety',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.Variety'),
        ),
        migrations.AddField(
            model_name='inventoryaction',
            name='variety',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='inventory.Variety'),
        ),
        migrations.AddField(
            model_name='crop',
            name='attributes',
            field=models.ManyToManyField(related_name='crops', to='inventory.CropAttributeOption'),
        ),
        migrations.AlterUniqueTogether(
            name='weekdayrequirement',
            unique_together={('plant_day', 'variety')},
        ),
    ]
