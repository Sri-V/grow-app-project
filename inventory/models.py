from django.db import models

class Variety(models.Model):
    """Represents the types of plants that can be grown."""
    name = models.CharField(max_length=50)
    alph_num_name = models.CharField(max_length=50, default="")  # Alphanumeric characters only, no spaces
    lead_time = models.IntegerField(null=True)  # Standard number of days to grow.

    def __str__(self):
        return self.name


class SanitationRecord(models.Model):
    """Represents a sanitation record of when the equipment has been sanitized for health inspectors"""
    date = models.DateField()
    employee_name = models.CharField(max_length=25)
    equipment_sanitized = models.CharField(max_length=100)
    chemicals_used = models.CharField(max_length=100)
    note = models.CharField(max_length=200, blank=True)


class ProductInventory(models.Model):
    """Represents the inventory of a type of product."""
    product = models.ForeignKey("orders.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()


class LiveCropInventory(ProductInventory):
    """Represents the inventory of a type of live microgreen crop"""
    seed_date = models.DateField()


class CropGroup(models.Model):
    """Represents a group of crops of a particular variety that share a seed date."""
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    seed_date = models.DateField()


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
    variety = models.ForeignKey(Variety, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ['plant_day', 'variety']

class KillReason(models.Model):
    """Represents a reason for trashing a crop."""
    name = models.CharField(max_length=200)

class InventoryAction(models.Model):
    ACTION_TYPES = (
        ('SEED', 'Seeded'),
        ('HARVEST', 'Harvested'),
        ('KILL', 'Killed'),
    )

    variety = models.ForeignKey(Variety, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    quantity = models.IntegerField(default=0, null=True)
    data = models.CharField(max_length=1000, null=True) # encode as a JSON with json.dumps({k:v,...})
    note = models.CharField(max_length=200, null=True)
    kill_reasons = models.ManyToManyField(KillReason, null=True) # on_delete=models.CASCADE