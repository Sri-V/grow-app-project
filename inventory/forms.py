from inventory.models import SanitationRecord
from django.forms import ModelForm, DateTimeField, DateTimeInput, Textarea, TextInput
from bootstrap_datepicker_plus import DatePickerInput


class SanitationRecordForm(ModelForm):
    # date = DateTimeField(input_formats=['%Y-%m-%d, %H:%M:%S'], widget=DatePickerInput(attrs={'class': 'form-control'}))
    class Meta:
        model = SanitationRecord
        fields = '__all__'
        widgets = {
            'date': DatePickerInput(),
            'employee_name': TextInput(attrs={'class': 'form-control'}),
            'equipment_sanitized': TextInput(attrs={'class': 'form-control'}),
            'chemicals_used': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control'}),
        }

