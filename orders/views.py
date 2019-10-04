from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from inventory.models import Crop, CropAttribute, CropAttributeOption, CropRecord, Slot, Variety, WeekdayRequirement, InventoryAction, KillReason, CropGroup, LiveCropInventory
from inventory.forms import *
from orders.models import LiveCropProduct, MicrogreenSize, TrayType, Product, HarvestedCropProduct
from datetime import date, datetime, timedelta
from dateutil import parser
from google_sheets.upload_to_sheet import upload_data_to_sheets
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import os
import json

@login_required
def shop(request):
    return render(request, "orders/shop.html", context={})
