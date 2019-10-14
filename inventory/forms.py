from inventory.models import Variety, SanitationRecord, KillReason
from orders.models import MicrogreenSize, TrayType
from django import forms
from django.forms import ModelForm, Textarea, TextInput
from django.core.exceptions import ValidationError
from bootstrap_datepicker_plus import DatePickerInput


class AddVarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = '__all__'
        labels = {
            'days_germ': 'Days in Germination:',
            'days_grow': 'Days in Grow:'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'form-add-variety-name', 'placeholder': 'e.g. Basil'}),
            'days_germ': forms.NumberInput(attrs={'class': 'form-control', 'id': 'form-add-variety-days-germ', 'min': '1'}),
            'days_grow': forms.NumberInput(attrs={'class': 'form-control', 'id': 'form-add-variety-days-grow', 'min': '1'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Variety.objects.filter(name=name).exists():
            raise ValidationError("Error: A variety with that name already exists", code="non-unique")
        else:
            return name


class SanitationRecordForm(ModelForm):
    class Meta:
        model = SanitationRecord
        fields = '__all__'
        widgets = {
            'date': DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                }),
            'employee_name': TextInput(attrs={'class': 'form-control'}),
            'equipment_sanitized': TextInput(attrs={'class': 'form-control'}),
            'chemicals_used': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control'}),
        }


class DateSeededForm(forms.Form):
    date_seeded = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
        },
        attrs={'class': 'form-control'}))


class InventoryKillCropForm(forms.Form):
    variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    date_killed = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
        },
        attrs={'class': 'form-control'}))
    date_seeded = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
        },
        attrs={'class': 'form-control'}))
    num_trays = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(InventoryKillCropForm, self).__init__(*args, **kwargs)
        for reason in KillReason.objects.all():
            self.fields[reason.name] = forms.BooleanField()


class AddProductForm(forms.Form):
    product_name = forms.CharField(max_length=200)
    price = forms.FloatField(min_value=0.0)

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


class AddLiveCropProductForm(forms.Form):
    product_name = forms.CharField(max_length=200)
    price = forms.FloatField(min_value=0.0)
    variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    size = forms.ModelChoiceField(queryset=MicrogreenSize.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    tray_type = forms.ModelChoiceField(queryset=TrayType.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-control'}))


class AddHarvestCropProductForm(forms.Form):
    product_name = forms.CharField(max_length=200)
    price = forms.FloatField(min_value=0.0)
    variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    size = forms.ModelChoiceField(queryset=MicrogreenSize.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    weight = forms.FloatField(min_value=0.0)