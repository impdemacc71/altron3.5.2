from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SKU, Batch, Barcode, TestQuestion, Test, TestAnswer, TestTemplate, TechnicalOutputChoice, BatchSpecTemplate # Import ALL Models

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

# 💡 NEW ADMIN: Batch Spec Template
@admin.register(BatchSpecTemplate)
class BatchSpecTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_fields')
    search_fields = ('name',)
    
    # Method to display the fields_json contents clearly
    def display_fields(self, obj):
        return ", ".join(obj.fields_json)
    display_fields.short_description = 'Required Specs'


class TestQuestionAdmin(admin.ModelAdmin):
    # Display the template and question text
    list_display = ['template', 'question_text', 'created_at']
    # Filter by template
    list_filter = ['template']
    # Search by question text and template name
    search_fields = ['question_text', 'template__name']


class TestAnswerInline(admin.TabularInline):
    model = TestAnswer
    extra = 0

class TestAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'sku', 'batch', 'template_used', 'overall_status', 'test_date', 'user']
    list_filter = ['overall_status', 'test_date', 'sku', 'batch', 'template_used']
    search_fields = ['barcode__sequence_number']
    inlines = [TestAnswerInline]

class BatchAdmin(admin.ModelAdmin):
    list_display = ['sku', 'prefix', 'batch_date', 'quantity', 'spec_template', 'created_at'] # Added spec_template
    list_filter = ['sku', 'batch_date', 'spec_template'] # Added spec_template
    search_fields = ['prefix']
    ordering = ['-created_at']

class BarcodeAdmin(admin.ModelAdmin):
    list_display = ['sequence_number', 'batch']
    list_filter = ['batch__sku']
    search_fields = ['sequence_number']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SKU)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Barcode, BarcodeAdmin)
admin.site.register(TestTemplate)
admin.site.register(TestQuestion, TestQuestionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(TestAnswer)


# 💡 Existing Admin for Technical Output Choices
@admin.register(TechnicalOutputChoice)
class TechnicalOutputChoiceAdmin(admin.ModelAdmin):
    list_display = ('value', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('value',)
    
    