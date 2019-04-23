from django.contrib import admin
from inventory.models import Crop, CropRecord, Slot, Variety

admin.site.register(Crop)
admin.site.register(CropRecord)
admin.site.register(Slot)
admin.site.register(Variety)