from django.contrib import admin
from inventory.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety, SanitationRecord, WeekdayRequirement, InventoryAction, KillReason, CropGroup

admin.site.register(Crop)
admin.site.register(CropAttribute)
admin.site.register(CropAttributeOption)
admin.site.register(CropRecord)
admin.site.register(Slot)
admin.site.register(Variety)
admin.site.register(SanitationRecord)
admin.site.register(WeekdayRequirement)
admin.site.register(InventoryAction)
admin.site.register(KillReason)
admin.site.register(CropGroup)