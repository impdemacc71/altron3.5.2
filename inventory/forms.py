
from django import forms
from .models import Batch, SKU

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['sku', 'batch_date', 'quantity', 'device_name', 'battery', 'capacity']
        widgets = {
            'batch_date': forms.DateInput(attrs={'type': 'date'}),
        }        