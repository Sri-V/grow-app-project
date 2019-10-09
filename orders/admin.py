from django.contrib import admin
from orders.models import TrayType, MicrogreenSize, Order, Product, LiveCropProduct, HarvestedCropProduct, RestaurantAccount

admin.site.register(Product)
admin.site.register(LiveCropProduct)
admin.site.register(HarvestedCropProduct)
admin.site.register(TrayType)
admin.site.register(MicrogreenSize)
admin.site.register(Order)
admin.site.register(RestaurantAccount)

