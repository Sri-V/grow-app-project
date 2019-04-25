from django.db import models

# Create your models here.


class Variety(models.Model):
    """Represents the types of plants that can be grown. Has a name and number of days between plant and harvest."""
    name = models.CharField(max_length=50)
    days_germ = models.IntegerField(null=True)
    days_grow = models.IntegerField(null=True)


class Crop(models.Model):
    """Represents a single attempt to grow a tray of Microgreens at a given time. Maintains a history of growth data
    in the form of sensor data, lifecycle advancements, tray movements, grower actions, and free-form notes.
    
    -> History recorded elsewhere, but linked by the crop's ID.
    """
    TRAY_SIZES = (
        ('1020', 'Standard - 10" × 20"'),
        ('1010', '10" × 10"'),
        ('0505', '5" × 5"'),
    )
    variety = models.ForeignKey(Variety, on_delete=models.PROTECT)
    tray_size = models.CharField(max_length=4, choices=TRAY_SIZES, default='1020')
    live_delivery = models.BooleanField(default=True)  # Do we deliver the live tray to the customer or cut it for them?
    # The number of days we plan to let the Crop germinate and grow, respectively
    # Different from the actual length of germination/grow time, encoded as CropRecords
    exp_num_germ_days = models.IntegerField()
    exp_num_grow_days = models.IntegerField()


class CropRecord(models.Model):
    """Represents a data point about a Crop at a particular moment in time. Has the property that a sorted
    list of all CropRecords describe the entire life of a plant from start to finish."""
    RECORD_TYPES = (
        ('SEED', 'Seeded'),
        ('GERM', 'Germinated/Sprouted'),
        ('GROW', 'Growth Milestone'),
        ('WATER', 'Watered'),
        ('HARVEST', 'Harvested'),
        ('DELIVERED', 'Delivered to Customer'),
        ('TRASH', 'Disposed'),
        ('RETURNED', 'Tray Returned'),
        ('NOTE', 'Notes')
    )
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES)
    note = models.CharField(max_length=200)


class Slot(models.Model):
    """Represents an address on a grow rack for a single Crop. Has a barcode, links to a Crop object, and is part
    of one or more Locations in the greenhouse hierarchy (e.g.: a rack or a shelf on a rack)."""
    barcode = models.CharField(max_length=50, blank=True, unique=True)
    # accurate
    current_crop = models.OneToOneField(Crop, on_delete=models.DO_NOTHING, blank=True, null=True)
    # location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)


class SanitationRecord(models.Model):
    """Represents a sanitation record of when the equipment has been sanitized for health inspectors"""
    date = models.DateTimeField()
    employee_name = models.CharField(max_length=25)
    equipment_sanitized = models.CharField(max_length=100)
    chemicals_used = models.CharField(max_length=100)
    note = models.CharField(max_length=200, blank=True)

