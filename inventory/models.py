from django.db import models
from django.utils import timezone
from .utils import generate_barcode

class SKU(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code

class Batch(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    batch_date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    device_name = models.CharField(max_length=100, blank=True)  # New field
    battery = models.CharField(max_length=100, blank=True)     # New field
    capacity = models.CharField(max_length=50, blank=True)     # New field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku.code} - {self.batch_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Get the last sequence number for this SKU
        last_barcode = Barcode.objects.filter(batch__sku=self.sku).order_by('-sequence_number').first()
        start_sequence = 1
        if last_barcode:
            # Extract the numeric part (e.g., '001' from 'KA0912HA001')
            last_number = int(last_barcode.sequence_number[-3:])
            start_sequence = last_number + 1
        # Generate sequence numbers and barcodes
        for i in range(self.quantity):
            sequence_number = f"{self.sku.code}HA{str(start_sequence + i).zfill(3)}"
            Barcode.objects.create(
                batch=self,
                sequence_number=sequence_number,
                barcode_image=generate_barcode(sequence_number)
            )

class Barcode(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    sequence_number = models.CharField(max_length=20, unique=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def __str__(self):
        return self.sequence_number