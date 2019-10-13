from django.db import models
from django.utils import timezone
from inventory.models import Variety


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
        # If germ_date exists, but grow_date does not => it has not been taken out of germ
        if self.germ_date() is not None and self.grow_date() is None:
            days_in_germ = timezone.now().date() - self.germ_date()
            return days_in_germ.days
        # If both dates exist, get the difference between them
        elif self.germ_date() is not None and self.grow_date() is not None:
            delta = self.grow_date() - self.germ_date()
            return delta.days
        else:
            return 0

    def days_in_grow(self):
        # If grow_date exists, but harvest_date does not => it has not been harvested
        if self.grow_date() is not None and self.harvest_date() is None:
            days_in_grow = timezone.now().date() - self.grow_date()
            return days_in_grow.days
        # If both dates exist, get the difference between them
        elif self.harvest_date() is not None and self.grow_date() is not None:
            delta = self.harvest_date() - self.grow_date()
            return delta.days
        else:
            return 0

    def germ_date(self):
        try:
            germ_record = self.crop_records.get(record_type='GERM')
            return germ_record.date
        except:
            return None

    def grow_date(self):
        try:
            grow_record = self.crop_records.get(record_type='GROW')
            return grow_record.date
        except:
            return None

    def harvest_date(self):
        try:
            harvest_record = self.crop_records.get(record_type='HARVEST')
            return harvest_record.date
        except:
            return None


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
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_records')
    date = models.DateField(default=timezone.now)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES)


class Slot(models.Model):
    """Represents an address on a grow rack for a single Crop. Has a barcode and links to a Crop object"""
    barcode = models.CharField(max_length=50, blank=True, unique=True)
    current_crop = models.OneToOneField(Crop, on_delete=models.DO_NOTHING, related_name='current_slot', blank=True, null=True)


