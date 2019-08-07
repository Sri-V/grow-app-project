from django.db import models
from django.utils import timezone


class Variety(models.Model):
    """Represents the types of plants that can be grown."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CropAttribute(models.Model):
    """Represent the an attribute abut a given crop that we would like to track. (e.g. Light height,
    soil type, substrate type, ect.)"""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CropAttributeOption(models.Model):
    """Represents a specific crop attribute type. For example if the CropAttribute was Light Type,
    then the CropAttributeOption's would be LED and T5."""
    attribute_group = models.ForeignKey(CropAttribute, related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Crop(models.Model):
    """Represents a single attempt to grow a tray of Microgreens at a given time. Maintains a history of growth data
    in the form of sensor data, lifecycle advancements, tray movements, grower actions, and free-form notes.
    
    -> History recorded as a CropRecord, but linked by the crop's ID.
    """

    variety = models.ForeignKey(Variety, on_delete=models.PROTECT)
    germ_date = models.DateField()  # date seeded and placed in germ
    grow_date = models.DateField()  # date placed on rack
    harvest_date = models.DateField(blank=True, null=True)
    crop_yield = models.FloatField(null=True, blank=True)  # measured in cm
    leaf_wingspan = models.FloatField(null=True, blank=True)  # measured in cm
    seeding_density = models.FloatField(null=True, blank=True)  # measured in g/tray
    attributes = models.ManyToManyField(CropAttributeOption, related_name='crops')
    notes = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # check that the crop has all the crop attributes that we have created
        # only needs to be checked on creation
        if not self.pk:
            # loops through all the crop attributes to make sure it has a value for each
            pass
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def days_in_germ(self):
        delta = self.grow_date - self.germ_date
        return delta.days

    def days_in_grow(self):
        if self.harvest_date is not None:
            delta = self.harvest_date - self.grow_date
            return delta.days
        else:
            return 0


class CropRecord(models.Model):
    """Represents a data point about a Crop at a particular moment in time. Has the property that a sorted
    list of all CropRecords describe the entire life of a plant from start to finish."""
    RECORD_TYPES = (
        ('GERM', 'Started Germination Phase'),
        ('GROW', 'Started Grow Phase'),
        ('WATER', 'Watered'),
        ('HARVEST', 'Harvested'),
        ('TRASH', 'Trashed'),
    )
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES)


class Slot(models.Model):
    """Represents an address on a grow rack for a single Crop. Has a barcode and links to a Crop object"""
    barcode = models.CharField(max_length=50, blank=True, unique=True)
    current_crop = models.OneToOneField(Crop, on_delete=models.DO_NOTHING, related_name='current_slot',  blank=True, null=True)


class SanitationRecord(models.Model):
    """Represents a sanitation record of when the equipment has been sanitized for health inspectors"""
    date = models.DateField()
    employee_name = models.CharField(max_length=25)
    equipment_sanitized = models.CharField(max_length=100)
    chemicals_used = models.CharField(max_length=100)
    note = models.CharField(max_length=200, blank=True)

class InHouse(models.Model):
    variety = models.OneToOneField(Variety, on_delete=models.PROTECT, primary_key=True)
    num_small = models.IntegerField(default=0)
    num_medium = models.IntegerField(default=0)
    num_big = models.IntegerField(default=0)
    
class WeekdayRequirement(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    plant_day = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    variety = models.ForeignKey(Variety, on_delete=models.PROTECT)
    num_small = models.IntegerField(default=0)
    num_medium = models.IntegerField(default=0)
    num_big = models.IntegerField(default=0)

    class Meta:
        unique_together = ['plant_day', 'variety']

class InventoryAction(models.Model):
    ACTION_TYPES = (
        ('SEED', 'Seeded'),
        ('HARVEST', 'Harvested'),
        ('KILL', 'Killed'),
    )

    variety = models.ForeignKey(Variety, on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now_add=True)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    data = models.CharField(max_length=1000, null=True) # encode as a JSON with json.dumps({k:v,...})
    note = models.CharField(max_length=200, null=True)