from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_batch, name='create_batch'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batch/<int:batch_id>/barcodes/', views.barcode_list, name='barcode_list'),
    path('batch/<int:batch_id>/print/', views.print_barcodes, name='print_barcodes'),
    path('batch/<int:batch_id>/print/<int:barcode_id>/', views.print_barcodes, name='print_single_barcode'),
]