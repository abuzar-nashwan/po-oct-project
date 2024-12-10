from django.shortcuts import render, redirect
from .forms import FileUploadForm
from pdf2image import convert_from_path
from django.shortcuts import render, redirect

from .forms import ImageUploadForm
from .models import UploadedImage
import po_meta_magic

def extract_text_from_pdf(file_path):
    extracted_data = []
    images = convert_from_path(file_path, fmt='png')
    meta_data = {
        'delivery_date': {
            "bbox": (0.35, 0.13, 0.64, 0.15),
            "key": 'Date of delivery',
            "date_format": '%d-%b-%y'
        },
        'delivery_address': {
            "bbox": (0.34, 0.17, 0.67, 0.25),
            "key": 'Delivery address',
            "optional_key_match": True
        },
        'po_number': {
            "bbox": (0.36, 0.10, 0.65, 0.12),
            "key": 'Order Number',
            "allowed_chars": '0-9A-Za-z'
        }
    }

    for image in images:
        extracted_text = po_meta_magic.extract_meta(image, meta_data)
        extracted_data.append(extracted_text)

    print(extracted_data)
    return extracted_data

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_path = uploaded_file.file.path
            extracted_data = extract_text_from_pdf(file_path)

            print("Extracted data: ", extracted_data)

            return render(request, 'ocr_app/result.html', {'data': extracted_data})
    else:
        form = FileUploadForm()
    return render(request, 'ocr_app/upload.html', {'form': form})


def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ImageUploadForm()
    images = UploadedImage.objects.all()
    return render(request, 'ocr_app/index.html', {'form': form, 'images': images})

# def index(request):
#     files = UploadedFile.objects.all()
#     files = [files[len(files) ]]
#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('index')
#     else:
#         form = FileUploadForm()
#     return render(request, 'ocr_app/index.html', {'form': form, 'files': files})
from pdf2image import convert_from_path
from PIL import Image
import os

def pdf_to_images(pdf_path, output_folder, width, height, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, image in enumerate(images):
        resized_image = image.resize((width, height), Image.LANCZOS)
        image_path = os.path.join(output_folder, f"page_{i + 1}.png")
        resized_image.save(image_path)
        print(f"Saved page {i + 1} as {image_path}")

pdf_path = "/Users/sivvi/Downloads/28-07-202418_00_19_913373_PurchaseorderTAFPO057947.pdf"
output_folder = "output_images"
desired_width = 600
desired_height = 600
pdf_to_images(pdf_path, output_folder, desired_width, desired_height, dpi=300)