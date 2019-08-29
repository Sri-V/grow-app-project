from django.contrib import admin
from inventory.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety, InHouse, SanitationRecord, WeekdayRequirement

admin.site.register(Crop)
admin.site.register(CropAttribute)
admin.site.register(CropAttributeOption)
admin.site.register(CropRecord)
admin.site.register(Slot)
admin.site.register(Variety)
admin.site.register(InHouse)
admin.site.register(SanitationRecord)
admin.site.register(WeekdayRequirement)