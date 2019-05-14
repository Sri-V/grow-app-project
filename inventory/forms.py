from inventory.models import SanitationRecord
from django.forms import ModelForm, Textarea, TextInput
from bootstrap_datepicker_plus import DatePickerInput


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

