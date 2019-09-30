from django.db import models
from inventory.models import Variety


class Account(models.Model):
    """Represents a customer of Boston Microgreens."""
    name = models.CharField(max_length=200)
    date_created = models.DateField(auto_now=True)
    active = models.BooleanField()


class Product(models.Model):
    """Represents a type of product to be sold."""
    name = models.CharField(max_length=200)
    price = models.FloatField()


class Order(models.Model):
    """Represents an sales order of product."""
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    delivery_date = models.DateField()


class TrayType(models.Model):
    """Represents a type of growing tray."""
    name = models.CharField(max_length=200)


class LiveCropProduct(Product):
    """Represents live tray microgreens products. Eg. 10 inch tray Sango"""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    size = models.CharField(max_length=40, choices=['SMALL', 'LARGE'])
    tray_type = models.ForeignKey(TrayType, on_delete=models.CASCADE)


class HarvestedCropProduct(Product):
    """Represents harvested microgreens products. Eg. 3oz clamshell of Shiso"""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    size = models.CharField(max_length=40, choices=['SMALL', 'LARGE'])
    weight = models.FloatField()

