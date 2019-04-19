from inventory.models import SanitationRecord
from django.forms import ModelForm, DateTimeField, DateTimeInput, Textarea, TextInput
from bootstrap_datepicker_plus import DateTimePickerInput


class SanitationRecordForm(ModelForm):
    class Meta:
        model = SanitationRecord
        fields = '__all__'
        widgets = {
            'date': DateTimePickerInput(
                options={
                     "format": "MM/DD/YYYY h:mm",
                 }),
            'employee_name': TextInput(attrs={'class': 'form-control'}),
            'equipment_sanitized': TextInput(attrs={'class': 'form-control'}),
            'chemicals_used': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control'}),
        }

