from inventory.models import Crop, CropAttribute, CropAttributeOption, Slot, Variety, SanitationRecord, CropRecord
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


class CropRecordForm(ModelForm):
    class Meta:
        model = CropRecord
        fields = ['record_type', 'date']
        widgets = {
            'record_type': forms.Select(choices=CropRecord.RECORD_TYPES, attrs={'class': 'form-control'}),
            'date': DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                }),
            # 'note': Textarea(attrs={'class': 'form-control', 'id': "form-add-crop-record-note", 'placeholder': "Add Note about crop record here"}),
        }


class CropNotesForm(ModelForm):
    class Meta:
        model = Crop
        fields = ['notes']
        widgets = {
            'notes': Textarea(attrs={'class': 'form-control', 'id': "form-add-crop-record-note", 'placeholder': "Add Note about crop here"}),
        }

class AddCropAttributesForm(ModelForm):
    class Meta:
        model = CropAttribute
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'id': "form-add-crop-attribute", 'placeholder': "E.g. (Light Type, Substrate, ect.)"})
        }

class AddAttributeOptionsForm(ModelForm):
    attribute_group = forms.ModelChoiceField(queryset=CropAttribute.objects.all(),
                           widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CropAttributeOption
        fields = ['attribute_group', 'name']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'id': "form-add-attribute-option"})
        }


class DateSeededForm(forms.Form):
    date_seeded = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
        },
        attrs={'class': 'form-control'}))

def generate_attributes():
    attributes = CropAttribute.objects.all()
    crop_attributes_list = []
    for attr in attributes:
        attribute_name = attr.name
        attribute_options = attr.options.all()
        choices_tuple = ()
        for option in attribute_options:
            choices_tuple += ((option.name, option.name),)
        select_tuple = (attribute_name, choices_tuple)
        crop_attributes_list.append(select_tuple)
    return crop_attributes_list

class NewCropForm(forms.Form):
    variety = forms.ModelChoiceField(queryset=Variety.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    date_seeded = forms.DateField(widget=DatePickerInput(
        options={
            "format": "MM/DD/YYYY",
        },
        attrs={'class': 'form-control'}))

    days_germinated = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        attrs = generate_attributes()
        super(NewCropForm, self).__init__(*args, **kwargs)
        for attribute in attrs:
            self.fields[attribute[0]] = forms.ChoiceField(choices=attribute[1], widget=forms.Select(attrs={'class': 'form-control'}))
        print(str(self.fields))


class HarvestCropForm(forms.Form):
    crop_yield = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the crop yield in cm'}))
    leaf_wingspan = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the leaf wingspan in cm'}))