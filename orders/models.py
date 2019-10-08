from django.db import models
from inventory.models import Variety
from django.contrib.auth.models import User


class RestaurantAccount(models.Model):
    """Represents a restaurant customer of Boston Microgreens."""
    phone = models.CharField(max_length=20)
    restaurant_name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    """Represents a type of product to be sold."""
    name = models.CharField(max_length=200)
    price = models.FloatField()


class Order(models.Model):
    """Represents an sales order of product."""
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    account = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    delivery_date = models.DateField()


class TrayType(models.Model):
    """Represents a type of growing tray."""
    name = models.CharField(max_length=200)


class MicrogreenSize(models.Model):
    name = models.CharField(max_length=200)


class LiveCropProduct(Product):
    """Represents live tray microgreens products. Eg. 10 inch tray Sango"""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    size = models.ForeignKey(MicrogreenSize, models.CASCADE)
    tray_type = models.ForeignKey(TrayType, on_delete=models.CASCADE)


class HarvestedCropProduct(Product):
    """Represents harvested microgreens products. Eg. 3oz clamshell of Shiso"""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    size = models.ForeignKey(MicrogreenSize, models.CASCADE)
    weight = models.FloatField()

