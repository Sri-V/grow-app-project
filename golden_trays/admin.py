from django.contrib import admin
from golden_trays.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot


admin.site.register(Crop)
admin.site.register(CropAttribute)
admin.site.register(CropAttributeOption)
admin.site.register(CropRecord)
admin.site.register(Slot)
