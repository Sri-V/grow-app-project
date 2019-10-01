# Generated by Django 2.1.5 on 2019-10-01 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('inventory', '0008_inventoryaction_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductInventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='LiveCropInventory',
            fields=[
                ('productinventory_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='inventory.ProductInventory')),
                ('seed_date', models.DateField()),
            ],
            bases=('inventory.productinventory',),
        ),
        migrations.AddField(
            model_name='productinventory',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Product'),
        ),
    ]
