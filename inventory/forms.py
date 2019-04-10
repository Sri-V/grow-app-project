from inventory.models import SanitationRecord
from django.forms import ModelForm, Textarea, TextInput

class SanitationRecordForm(ModelForm):
    class Meta:
        model = SanitationRecord
        fields = ['date', 'employee_name', 'equipment_sanitized', 'chemicals_used', 'note']
        widgets = {
            'date': TextInput(attrs={'class': 'form-control'}),
            'employee_name': TextInput(attrs={'class': 'form-control'}),
            'equipment_sanitized': TextInput(attrs={'class': 'form-control'}),
            'chemicals_used': TextInput(attrs={'class': 'form-control'}),
            'note': Textarea(attrs={'class': 'form-control'}),
        }