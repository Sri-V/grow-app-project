from inventory.models import Crop, Slot, Variety
from django import forms
from django.core.exceptions import ValidationError
from bootstrap_datepicker_plus import DateTimePickerInput


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



class NewCropForm(forms.Form):
    variety = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=Variety.objects.all(),
    )


