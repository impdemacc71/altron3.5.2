import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile

def generate_barcode(sequence_number):
    # Generate Code128 barcode
    code128 = barcode.get_barcode_class('code128')
    barcode_instance = code128(sequence_number, writer=ImageWriter())
    
    # Save barcode to a BytesIO buffer
    buffer = BytesIO()
    barcode_instance.write(buffer, options={"write_text": True})
    
    # Create a ContentFile for Django's ImageField
    filename = f"{sequence_number}.png"
    return ContentFile(buffer.getvalue(), name=filename)