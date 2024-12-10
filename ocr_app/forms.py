# ocr_app/forms.py

from django import forms
from .models import UploadedFile
from .models import UploadedImage

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image']