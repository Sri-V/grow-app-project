from django.db import models

# Create your models here.


class Crop(models.Model):
    """Represents a single attempt to grow a tray of Microgreens at a given time. Maintains a history of growth data
    in the form of sensor data, lifecycle advancements, tray movements, grower actions, and free-form notes.
    
    -> History recorded elsewhere, but linked by the crop's ID.
    """

    variety = models.ForeignKey(Variety)
    days_germ = models.IntegerField()
    days_grow = models.IntegerField()
    harvest_in_house = models.BooleanField(default=False)
    pass


class CropRecord(models.Model):
    """Represents a data point about a Crop at a particular moment in time. Has the property that a sorted
    list of all CropRecords describe the entire life of a plant from start to finish."""
    RECORD_TYPES = (
        ('WATER', 'Water'),
        ('PLANT', 'Planted'),
        ('GERM', 'Began Gernmination Phase'),
        ('GROW', 'Began Grow Phase'),
        ('HARVEST', 'Harvested'),
        ('DELIVERED', 'Delivered to Customer'),
        ('TRASH', 'Disposed'),
        ('RETURNED', 'Tray Returned'),
        ('NOTE', 'Notes')
    )
    crop = models.ForeignKey(Crop)
    date = models.DateField()
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES)
    note = models.CharField(max_length=200)

class Location(models.Model):
    """Represents the physical location of a Tray. Can be a Slot in-house, or Customer upon delivery."""
    LOCATION_TYPES = (
        ('CUST', 'Customer'),
        ('SLOT', 'Slot')
    )
    name = models.CharField(max_length=60)
    location_type = models.CharField(max_length=4, choices=LOCATION_TYPES)

class Order(models.Model):
    """Represents a Customer's order, with details necessary for generating Crops and tasks. Implement later."""
    pass

class Tray(models.Model):
    """Represents the container in which a crop is grown. Has a barcode, current Crop, and Location."""
    TRAY_SIZES = (
        ('1020', 'Standard - 10x20"'),
        ('1010', '10x10"'),
        ('0505', '5x5"'),
    )
    barcode = models.charField(max_length=50)
    current_crop = models.OneToOneField(Crop, on_delete=models.DO_NOTHING, blank=True, null=True)
    size = models.CharField(max_length=4, choices=TRAY_SIZES, default='1010')
    location = models.ForeignKey(Location)

class Variety(models.Model):
    """Represents the types of plants that can be grown. Has a name and number of days between plant and harvest."""
    name = models.CharField(max_length=50)
    days_plant_to_harvest = models.IntegerField()