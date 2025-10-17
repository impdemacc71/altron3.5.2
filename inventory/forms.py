import string
from django import forms
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .models import CustomUser, SKU, Batch, Barcode, Test, TestQuestion, TestAnswer, TestTemplate, TechnicalOutputChoice, BatchSpecTemplate 

# Define all possible spec field mappings (Internal Name: Human Readable Label)
SPEC_FIELD_MAP = {
    # ... (map remains the same)
    'device_name': 'Device Name',
    'battery': 'Battery',
    'capacity': 'BATTERY Cap',         
    'mppt_cap': 'MPPT Cap',
    'voc_max': 'Voc Max',             
    'feature_spec': 'Feature / Spec',
    'ef': 'EF',
    
    # New Fields Mapped:
    'system_cap': 'SYSTEM Cap',       
    'spv_max': 'SPV Max',             
    'dc_load': 'DC LOAD',             
    'kel_po': 'KEL-PO',               
    'current_max': 'CURRENT Max',     
    'input_range': 'INPUT Range',     
    'output_range': 'OUTPUT Range',   
}

class BatchCreateForm(forms.ModelForm):
    # Field to select the template (must be a visible ModelChoiceField)
    spec_template = forms.ModelChoiceField(
        queryset=BatchSpecTemplate.objects.all(),
        required=True,
        label="Select Specification Template",
        empty_label="--- Select Template ---",
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md', 'id': 'id_spec_template'})
    )
    
    # Prefix field is required for the save logic but not listed in Meta.fields
    # We must define it here to access it in __init__ and save()
    prefix = forms.CharField(max_length=20, required=False) 


    class Meta:
        model = Batch
        # These are the CORE fields always needed for batch/barcode creation.
        # Note: Prefix is defined above, not here.
        fields = ['sku', 'batch_date', 'quantity', 'spec_template'] 
        widgets = {
            'sku': forms.Select(attrs={'class': 'w-full p-2 border rounded-md'}),
            'batch_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-md'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Ensure prefix is correctly initialized from instance if editing
        if self.instance.pk:
            self.fields['prefix'].initial = self.instance.prefix
        
        # 2. Determine the template ID
        template_id = None
        if self.is_bound and self.data.get('spec_template'):
            template_id = self.data['spec_template']
        elif self.instance.pk and self.instance.spec_template:
            template_id = self.instance.spec_template.pk
        
        required_fields = []
        if template_id:
            try:
                template = BatchSpecTemplate.objects.get(pk=template_id)
                required_fields = template.fields_json 
            except BatchSpecTemplate.DoesNotExist:
                pass
        
        # 3. Add dynamic spec fields
        for field_name in SPEC_FIELD_MAP.keys():
            if field_name in self.fields:
                del self.fields[field_name]

        if required_fields:
            for field_name in required_fields:
                label = SPEC_FIELD_MAP.get(field_name, field_name.replace('_', ' ').title())
                
                initial_value = self.instance.__dict__.get(field_name) if self.instance else None
                is_required = field_name not in ['feature_spec', 'ef']
                
                self.fields[field_name] = forms.CharField(
                    label=label,
                    required=is_required,
                    initial=initial_value,
                    widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md'})
                )

    # 💡 CRITICAL FIX: Override save to manually transfer validated dynamic data
    def save(self, commit=True):
        # 1. Call ModelForm save method but prevent saving to DB immediately
        instance = super().save(commit=False) 

        # 2. Loop through dynamic fields and assign validated data
        if instance.spec_template:
            required_fields = instance.spec_template.fields_json
            
            for field_name in required_fields:
                # We only need to check fields that were actually rendered and validated
                if field_name in self.cleaned_data:
                    # Assign the validated data from the form to the model instance attribute
                    setattr(instance, field_name, self.cleaned_data[field_name])
                # Ensure the prefix is also set, as it's not in Meta.fields
                elif field_name == 'prefix':
                    setattr(instance, 'prefix', self.cleaned_data['prefix'])

        # 3. Handle the prefix field explicitly if not handled in the loop (recommended practice)
        if 'prefix' in self.cleaned_data:
             instance.prefix = self.cleaned_data['prefix']
             
        # 4. Save the instance with all dynamic data
        if commit:
            instance.save() 
        return instance

# TestForm remains unchanged from the previous working version
class TestForm(forms.Form):
    sku = forms.ModelChoiceField(
        queryset=SKU.objects.all(),
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), # Initial queryset, will be filtered in __init__
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    barcode = forms.ModelChoiceField(
        queryset=Barcode.objects.all(), # Initial queryset, will be filtered in __init__
        required=False, # Barcode is optional
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    template = forms.ModelChoiceField(
        queryset=TestTemplate.objects.all(),
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    overall_status = forms.ChoiceField(
        choices=[('pending', 'Pending'), ('passed', 'Passed'), ('failed', 'Failed')],
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )

    def __init__(self, *args, **kwargs):
        # Pop custom arguments before calling super().__init__
        selected_sku_id = kwargs.pop('selected_sku_id', None)
        selected_batch_id = kwargs.pop('selected_batch_id', None)
        selected_template_id = kwargs.pop('selected_template_id', None)
        
        super().__init__(*args, **kwargs)

        # Filter Batch choices based on selected SKU
        if selected_sku_id:
            self.fields['batch'].queryset = Batch.objects.filter(sku_id=selected_sku_id)
        else:
            self.fields['batch'].queryset = Batch.objects.none()

        # Filter Barcode choices based on selected Batch
        if selected_batch_id:
            self.fields['barcode'].queryset = Barcode.objects.filter(batch_id=selected_batch_id)
        else:
            self.fields['barcode'].queryset = Barcode.objects.none()
        
        
        # FINAL FIX: Use a comprehension to guarantee clean (value, label) tuples
        dynamic_outputs_list = [
            (choice.value, choice.value)
            for choice in TechnicalOutputChoice.objects.filter(is_active=True).order_by('order', 'value')
        ]
        
        TECHNICAL_OUTPUT_CHOICES = [
            ('', '--- Select Output ---'),
        ]
        
        # Extend the list with the dynamic choices.
        TECHNICAL_OUTPUT_CHOICES.extend(dynamic_outputs_list)
        # Dynamically add TestQuestion fields if a Template is selected
        current_template_id = selected_template_id or (self.data.get('template') if 'template' in self.data else None)

        if current_template_id:
            try:
                template_instance = TestTemplate.objects.get(pk=current_template_id)
                questions = TestQuestion.objects.filter(template=template_instance).order_by('id')
                for question in questions:
                    self.fields[f'question_{question.id}_status'] = forms.ChoiceField(
                        choices=[('fail', 'Fail'), ('pass', 'Pass')],
                        label=question.question_text,
                        widget=forms.Select(attrs={
                            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
                        })
                    )
                    
                    # NEW TECHNICAL OUTPUT FIELD - NOW USES DYNAMIC CHOICES
                    self.fields[f'question_{question.id}_output'] = forms.ChoiceField(
                        choices=TECHNICAL_OUTPUT_CHOICES, 
                        required=False,
                        label='',
                        widget=forms.Select(attrs={
                            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
                        })
                    )
                    self.fields[f'question_{question.id}_remarks'] = forms.CharField(
                        required=False,
                        label='',
                        widget=forms.Textarea(attrs={
                            'rows': 3,
                            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                            'placeholder': 'Add remarks here...'
                        })
                    )
            except TestTemplate.DoesNotExist:
                pass
        
        # Ensure initial values are set correctly for dropdowns if they exist in initial data
        if self.initial.get('sku'):
            self.fields['batch'].queryset = Batch.objects.filter(sku_id=self.initial['sku'])
        
        if self.initial.get('batch'):
            self.fields['barcode'].queryset = Barcode.objects.filter(batch_id=self.initial['batch'])


# This is the dedicated form for updating overall status on the test_detail page
class TestOverallStatusForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['overall_status']
        widgets = {
            'overall_status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm py-2.5 px-3 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'
            }),
        }