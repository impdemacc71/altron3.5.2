from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SKU, Batch, Barcode

admin.site.register(SKU)
admin.site.register(Batch)
admin.site.register(Barcode)