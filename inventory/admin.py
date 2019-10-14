from django.contrib import admin
from inventory.models import Variety, SanitationRecord, WeekdayRequirement, InventoryAction, KillReason, CropGroup
from orders.models import TrayType, MicrogreenSize, Order, Product, LiveCropProduct, HarvestedCropProduct

admin.site.register(Variety)
admin.site.register(SanitationRecord)
admin.site.register(WeekdayRequirement)
admin.site.register(InventoryAction)
admin.site.register(KillReason)
admin.site.register(CropGroup)
admin.site.register(Product)
admin.site.register(LiveCropProduct)
admin.site.register(HarvestedCropProduct)
admin.site.register(TrayType)
admin.site.register(MicrogreenSize)
admin.site.register(Order)
