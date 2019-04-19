from inventory.models import Variety
from django.forms import ModelForm, DateTimeField, DateTimeInput, Textarea, TextInput, NumberInput
from bootstrap_datepicker_plus import DateTimePickerInput


class AddVarietyForm(ModelForm):
    class Meta:
        model = Variety
        fields = '__all__'
        labels = {
            'days_plant_to_harvest':'Days Until Harvest:'
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'id':'form-add-variety-name', 'placeholder': 'e.g. Basil'}),
            'days_plant_to_harvest': NumberInput(attrs={'class': 'form-control', 'id':'form-add-variety-days-to-harvest', 'min': '1'}),
        }
