from orders.models import RestaurantAccount, Product, Order, LiveCropProduct, TrayType, HarvestedCropProduct, \
    MicrogreenSize
from inventory.models import Crop, CropAttribute, CropAttributeOption, Slot, Variety, SanitationRecord, CropRecord, \
    KillReason
from django import forms
from django.forms import ModelForm, Textarea, TextInput
from django.core.exceptions import ValidationError
from bootstrap_datepicker_plus import DatePickerInput
from datetime import date, datetime, timedelta


def getNonDeliveryDays():
    return [0, 1, 3, 4, 6]


class OrderForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    quantity = forms.IntegerField(min_value=0)
    delivery_date = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
            "daysOfWeekDisabled": getNonDeliveryDays()
            # "minDate": str(date.today()),
        },
        attrs={'class': 'form-control'}))

