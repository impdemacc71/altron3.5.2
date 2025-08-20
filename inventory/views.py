from django.shortcuts import render, redirect, get_object_or_404
from .forms import BatchForm
from .models import Batch, Barcode, SKU

def create_batch(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('batch_list')
    else:
        form = BatchForm()
    return render(request, 'inventory/create_batch.html', {'form': form})

def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'inventory/batch_list.html', {'batches': batches})

def barcode_list(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    barcodes = Barcode.objects.filter(batch=batch)
    return render(request, 'inventory/barcode_list.html', {'batch': batch, 'barcodes': barcodes})

def print_barcodes(request, batch_id, barcode_id=None):
    batch = get_object_or_404(Batch, id=batch_id)
    if barcode_id:
        barcodes = [get_object_or_404(Barcode, id=barcode_id, batch=batch)]
    else:
        barcodes = Barcode.objects.filter(batch=batch)
    return render(request, 'inventory/print_barcodes.html', {'batch': batch, 'barcodes': barcodes})