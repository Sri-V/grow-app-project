from inventory.models import SanitationRecord
from django.forms import ModelForm


class SanitationRecordForm(ModelForm):
    class Meta:
        model = SanitationRecord
        fields = ['date', 'employee_name', 'equipment_sanitized', 'chemicals_used', 'note']