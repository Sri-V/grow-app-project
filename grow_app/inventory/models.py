from django.db import models

# Create your models here.


class Crop(models.Model):
    """Represents a single attempt to grow a tray of Microgreens at a given time. Maintains a history of growth data
    in the form of sensor data, lifecycle advancements, tray movements, grower actions, and free-form notes."""
    pass


class CropRecord(models.Model):
    """Represents a data point about a Crop at a particular moment in time. Has the property that a sorted
    list of all CropRecords describe the entire life of a plant from start to finish."""
    crop = models.ForeignKey(Crop)


class Tray(models.Model):
    """Represents a space in the greenhouse as opposed to a particular plant. Receives any growing actions that can be
    performed on a plant in the greenhouse"""
    current_crop = models.OneToOneField(Crop, on_delete=models.CASCADE())
