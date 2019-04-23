from inventory.models import Variety
from django.forms import ModelForm, DateTimeField, DateTimeInput, Textarea, TextInput, NumberInput
from django.core.exceptions import ValidationError
from bootstrap_datepicker_plus import DateTimePickerInput


class AddVarietyForm(ModelForm):
    class Meta:
        model = Variety
        fields = '__all__'
        labels = {
            'days_germ':'Days in Germination:',
            'days_grow':'Days in Grow:'
        }
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'id':'form-add-variety-name', 'placeholder': 'e.g. Basil'}),
            'days_germ': NumberInput(attrs={'class': 'form-control', 'id':'form-add-variety-days-germ', 'min': '1'}),
            'days_grow': NumberInput(attrs={'class': 'form-control', 'id':'form-add-variety-days-grow', 'min': '1'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        print(Variety.objects.filter(name=name))
        print(Variety.objects.filter(name=name).exists())
        if Variety.objects.filter(name=name).exists():
            raise ValidationError("Error: A variety with that name already exists")
        else:
            return name


