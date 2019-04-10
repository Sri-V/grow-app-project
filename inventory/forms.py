from inventory.models import SanitationRecord
from django.forms import ModelForm, DateTimeField, DateTimeInput, Textarea, TextInput, widgets

class SanitationRecordForm(ModelForm):
    date = DateTimeField(input_formats=['%Y-%m-%d, %H:%M:%S'])
    class Meta:
        model = SanitationRecord
        fields = '__all__'
        widgets = {
            'date': DateTimeInput(attrs={'class': 'form-control'}),
            'employee_name': TextInput(attrs={'class': 'form-control'}),
            'equipment_sanitized': TextInput(attrs={'class': 'form-control'}),
            'chemicals_used': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control'}),
        }