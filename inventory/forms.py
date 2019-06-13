from inventory.models import Crop, Slot, Variety, SanitationRecord, CropRecord
from django import forms
from django.forms import ModelForm, Textarea, TextInput
from django.core.exceptions import ValidationError
from bootstrap_datepicker_plus import DatePickerInput


class AddVarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = '__all__'
        labels = {
            'days_germ':'Days in Germination:',
            'days_grow':'Days in Grow:'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id':'form-add-variety-name', 'placeholder': 'e.g. Basil'}),
            'days_germ': forms.NumberInput(attrs={'class': 'form-control', 'id':'form-add-variety-days-germ', 'min': '1'}),
            'days_grow': forms.NumberInput(attrs={'class': 'form-control', 'id':'form-add-variety-days-grow', 'min': '1'}),
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

class CropRecordForm(ModelForm):
    class Meta:
        model = CropRecord
        fields = ['record_type', 'date', 'note']
        widgets = {
            'record_type': forms.Select(choices=CropRecord.RECORD_TYPES,attrs={'class': 'form-control'}),
            'date': DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                }),
            'note': Textarea(attrs={'class': 'form-control', 'id': "form-add-crop-record-note", 'placeholder': "Add Note about crop record here"}),
        }

class DateSeededForm(forms.Form):
    date_seeded = forms.DateField(widget=DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                },
                attrs={'class': 'form-control'}))
