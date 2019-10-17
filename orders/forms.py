from orders.models import RestaurantAccount, Product, Order, LiveCropProduct, TrayType, HarvestedCropProduct, \
    MicrogreenSize, Tag
from inventory.models import Variety, SanitationRecord, KillReason
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


class AddProductForm(forms.Form):
    product_name = forms.CharField(max_length=200)
    price = forms.FloatField(min_value=0.0)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))

    def get_live_crop_fields(self):
        variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                         widget=forms.Select(attrs={'class': 'form-control'}))
        size = forms.ModelChoiceField(queryset=MicrogreenSize.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}))
        tray_type = forms.ModelChoiceField(queryset=TrayType.objects.all(),
                                           widget=forms.Select(attrs={'class': 'form-control'}))
        return [variety, size, tray_type]

    def get_harvested_crop_fields(self):
        variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                         widget=forms.Select(attrs={'class': 'form-control'}))
        size = forms.ModelChoiceField(queryset=MicrogreenSize.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}))
        weight = forms.FloatField(min_value=0.0)
        return [variety, size, weight]
