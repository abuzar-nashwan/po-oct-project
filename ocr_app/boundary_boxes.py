from datetime import datetime
from dateutil import parser
import pytesseract
from PIL import Image
import os
from functools import wraps
import re

def validate_inputs(func):
    """
    Decorator to validate inputs for the extract_meta function.

    Validates that:
    - The image is not None.
    - The meta_data is a dictionary.
    - Each value in meta_data is a dictionary containing a 'bbox' tuple and a 'key' string.

    Adds any validation errors to an 'errors' attribute on the function.
    """
    @wraps(func)
    def wrapper(image, meta_data=None):
        wrapper.errors = []  # Initialize an empty list for errors

        if image is None:
            wrapper.errors.append("Image must be provided and cannot be None.")

        if not isinstance(meta_data, dict):
            wrapper.errors.append("meta_data must be a dictionary.")
        else:
            for key, value in meta_data.items():
                if not isinstance(value, dict):
                    wrapper.errors.append(f"Value for '{key}' must be a dictionary.")
                else:
                    bbox = value.get('bbox')
                    key_value = value.get('key')

                    if not isinstance(bbox, tuple):
                        wrapper.errors.append(f"'bbox' for '{key}' must be a tuple.")

                    if not isinstance(key_value, str):
                        wrapper.errors.append(f"'key' for '{key}' must be a string.")

        return func(image, meta_data)
    return wrapper

@validate_inputs
def extract_meta(image, meta_data=None):
    if extract_meta.errors:
        print("Validation Errors:")
        return extract_meta.errors

    extracted_data = {}

    for idx_key, values in meta_data.items():
        bbox = values['bbox']
        key = values['key']
        date_format = values.get('date_format', None)
        optional_key_match = values.get('optional_key_match', False)
        allowed_chars = values.get('allowed_chars', None)

        cleaned_text = extract_meta_data(image, bbox, key, optional_key_match)

        if date_format:
            cleaned_text = make_required_format(cleaned_text, date_format)

        if allowed_chars:
            cleaned_text = keep_allowed_chars(cleaned_text, allowed_chars)

        extracted_data[idx_key] = cleaned_text

    return extracted_data


def keep_allowed_chars(text, allowed_chars):
    pattern = f'[^{allowed_chars}]'
    return re.sub(pattern, '', text)

# meta_data = {
#  'delivery_date': {
#         "bbox": (),
#         "key": '',
#         "date_format" : ''
#      },
# 'delivery_address': {
#         "bbox": (),
#         "key": '',
#         "optional_key_match": True
#     },
# 'po_number': {
#         "bbox": (),
#         "key": '',
#     }
# }

### PRIVATE METHODS

def extract_meta_data(image, bbox, key, optional_key_match, retry=0):
    img_width, img_height = image.size
    start_x = bbox[0] * img_width
    start_y = bbox[1] * img_height
    end_x = bbox[2] * img_width
    end_y = bbox[3] * img_height

    cropped_image = image.crop((start_x, start_y, end_x, end_y))
    cropped_image.save(f'output_images/file{datetime.now()}.jpg')
    text = pytesseract.image_to_string(cropped_image)
    text = text.strip()

    removed_key_text = find_and_remove_key(text, key, optional_key_match)
    if not removed_key_text and retry<5:
        bigger_bbox = increase_bounding_box(bbox)
        return extract_meta_data(image, bigger_bbox, key, optional_key_match, retry+1)

    return removed_key_text

def make_required_format(date_text, required_format):
    try:
        parsed_date = parser.parse(date_text, fuzzy=True)
        formatted_date = parsed_date.strftime(required_format)
        return formatted_date
    except ValueError:
        raise ValueError("Date format not recognized")

def increase_bounding_box(bbox, increase_factor=0.1):
    x_min, y_min, x_max, y_max = bbox

    width = x_max - x_min
    height = y_max - y_min

    new_width = width * (1 + increase_factor)
    new_height = height * (1 + increase_factor)

    width_increase = (new_width - width) / 2
    height_increase = (new_height - height) / 2

    new_x_min = max(0, x_min - width_increase)
    new_y_min = max(0, y_min - height_increase)
    new_x_max = min(1, x_max + width_increase)
    new_y_max = min(1, y_max + height_increase)

    if new_x_min < 0:
        new_x_max -= new_x_min
        new_x_min = 0
    if new_y_min < 0:
        new_y_max -= new_y_min
        new_y_min = 0
    if new_x_max > 1:
        new_x_min -= (new_x_max - 1)
        new_x_max = 1
    if new_y_max > 1:
        new_y_min -= (new_y_max - 1)
        new_y_max = 1

    return (new_x_min, new_y_min, new_x_max, new_y_max)

def find_and_remove_key(text, key, optional_key_match):
    if optional_key_match:
        return text

    if key in text:
        text = text.replace(key, '')
        return text

    return ''

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

# from datetime import datetime
# from dateutil import parser
# import pytesseract
# from PIL import Image
# import os


# from functools import wraps

# def validate_inputs(func):
#     """
#     Decorator to validate inputs for the extract_meta function.

#     Validates that:
#     - The image is not None.
#     - The meta_data is a dictionary.
#     - Each value in meta_data is a dictionary containing a 'bbox' tuple and a 'key' string.

#     Adds any validation errors to an 'errors' attribute on the function.
#     """
#     @wraps(func)
#     def wrapper(image, meta_data=None):
#         wrapper.errors = []  # Initialize an empty list for errors

#         if image is None:
#             wrapper.errors.append("Image must be provided and cannot be None.")

#         if not isinstance(meta_data, dict):
#             wrapper.errors.append("meta_data must be a dictionary.")
#         else:
#             for key, value in meta_data.items():
#                 if not isinstance(value, dict):
#                     wrapper.errors.append(f"Value for '{key}' must be a dictionary.")
#                 else:
#                     bbox = value.get('bbox')
#                     key_value = value.get('key')

#                     if not isinstance(bbox, tuple):
#                         wrapper.errors.append(f"'bbox' for '{key}' must be a tuple.")

#                     if not isinstance(key_value, str):
#                         wrapper.errors.append(f"'key' for '{key}' must be a string.")

#         return func(image, meta_data)
#     return wrapper


# # meta_data = {
# #  'delivery_date': {
# #         "bbox": (),
# #         "key": '',
# #         "format" : ''
# #      },
# # 'delivery_address': {
# #         "bbox": (),
# #         "key": '',
# #         "optional_key_match": True
# #     },
# # 'po_number': {
# #         "bbox": (),
# #         "key": '',
# #     }
# # }
# @validate_inputs
# def extract_meta(image, meta_data=None):
#     if extract_meta.errors:
#         print("Validation Errors:")
#         return extract_meta.errors

#     extracted_data = {}

#     for idx_key, values in meta_data.items():
#         bbox = values['bbox']
#         key = values['key']
#         date_format = values.get('format', None)
#         optional_key_match = values.get('optional_key_match', False)

#         cleaned_text = extract_meta_data(image, bbox, key, optional_key_match)

#         if date_format:
#             cleaned_text = make_required_format(cleaned_text, date_format)

#         extracted_data[idx_key] = cleaned_text

#     return extracted_data



# ### PRIVATE METHODS

# def extract_meta_data(image, bbox, key, optional_key_match, retry=0):
#     img_width, img_height = image.size
#     start_x = bbox[0] * img_width
#     start_y = bbox[1] * img_height
#     end_x = bbox[2] * img_width
#     end_y = bbox[3] * img_height

#     cropped_image = image.crop((start_x, start_y, end_x, end_y))
#     text = pytesseract.image_to_string(cropped_image)
#     text = text.strip()

#     removed_key_text = find_and_remove_key(text, key, optional_key_match)
#     if not removed_key_text:
#         bigger_bbox = increase_bounding_box(bbox)
#         return extract_meta_data(image, bigger_bbox, key, optional_key_match, retry+1)

#     return removed_key_text

# def make_required_format(date_text, required_format):
#     try:
#         parsed_date = parser.parse(date_text, fuzzy=True)
#         formatted_date = parsed_date.strftime(required_format)
#         return formatted_date
#     except ValueError:
#         raise ValueError("Date format not recognized")

# def increase_bounding_box(bbox, increase_factor=0.1):
#     x_min, y_min, x_max, y_max = bbox

#     width = x_max - x_min
#     height = y_max - y_min

#     new_width = width * (1 + increase_factor)
#     new_height = height * (1 + increase_factor)

#     width_increase = (new_width - width) / 2
#     height_increase = (new_height - height) / 2

#     new_x_min = max(0, x_min - width_increase)
#     new_y_min = max(0, y_min - height_increase)
#     new_x_max = min(1, x_max + width_increase)
#     new_y_max = min(1, y_max + height_increase)

#     if new_x_min < 0:
#         new_x_max -= new_x_min
#         new_x_min = 0
#     if new_y_min < 0:
#         new_y_max -= new_y_min
#         new_y_min = 0
#     if new_x_max > 1:
#         new_x_min -= (new_x_max - 1)
#         new_x_max = 1
#     if new_y_max > 1:
#         new_y_min -= (new_y_max - 1)
#         new_y_max = 1

#     return (new_x_min, new_y_min, new_x_max, new_y_max)

# def find_and_remove_key(text, key, optional_key_match):
#     if optional_key_match:
#         return True

#     if key in text:
#         text = text.replace(key, '')
#         return text

#     return ''




# # meta_data = {
# #  'delivery_date': {
# #         "bbox": (),
# #         "key": '',
# #         "format" : ''
# #      },
# # 'delivery_address': {
# #         "bbox": (),
# #         "key": '',
# #     },
# # 'po_number': {
# #         "bbox": (),
# #         "key": '',
# #     }
# # }
# # returns {
# #     "po_number": "",
# #     "delivery_date": "",
# #     "delivery_address": "",
# # }


# # # Ensure directories exist
# # os.makedirs('before', exist_ok=True)
# # os.makedirs('cropped', exist_ok=True)
# # os.makedirs('processed', exist_ok=True)




# # # 04-06-202414_39_00_506510C11550 (1).pdf
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'location': (0.70, 0.06, 0.91, 0.10), 'required_format': 'Number'},
# #         'PO_DELIVERY_DATE': {'location': (0.66, 0.11, 0.97, 0.15), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'location': (0.32, 0.18, 0.63, 0.33), 'required_format': 'String'}
# #     },
# # ]

# # # Test 2.pdf
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'location': (0.04, 0.07, 0.29, 0.10), 'required_format': 'Number'},
# #         'PO_DELIVERY_DATE': {'location': (0.46, 0.43, 0.89, 0.50), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'location': (0.66, 0.17, 0.89, 0.31), 'required_format': 'String'}
# #     }
# # ]

# # /Users/sivvi/Documents/repos/tesseract-exp/ocr_project/22-07-202416_00_11_15554211170188938901SGVSN4.pdf
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'key': '', 'location': (0.36, 0.09, 0.64, 0.12)},
# #         'PO_DELIVERY_DATE': {'key': '', 'location': (0.36, 0.13, 0.64, 0.15), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'key': '', 'location': (0.37, 0.17, 0.64, 0.25)}
# #     }
# # ]

# # # /Users/sivvi/Documents/repos/tesseract-exp/ocr_project/22-07-202416_00_11_15554211170188938901SGVSN4.pdf
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'location': (0.50, 0.2, 0.8, 0.2), 'required_format': 'Number'},
# #         'PO_DELIVERY_DATE': {'location': (0.50, 0.20, 0.75, 0.25), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'location': (0.47, 0.27, 0.74, 0.45), 'required_format': 'String'}
# #     }
# # ]

# # # /Users/sivvi/Documents/repos/tesseract-exp/ocr_project/22-07-202416_10_17_687386PurchaseOrder4030254445.PDF
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'location': (0.48, 0.16, 0.67, 0.18), 'required_format': 'Number'},
# #         'PO_DELIVERY_DATE': {'location': (0.46, 0.18, 0.72, 0.20), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'location': (0.02, 0.26, 0.45, 0.32), 'required_format': 'String'}
# #     }
# # ]

# # # /Users/sivvi/Downloads/22-07-202416_10_28_380233PO474558mkark115172164971312273N6000250429.pdf
# # bounding_boxes = [
# #     {
# #         'PO_NUM': {'location': (0.07, 0.11, 0.33, 0.13), 'required_format': 'Number'},
# #         'PO_DELIVERY_DATE': {'location': (0.49, 0.10, 0.79, 0.14), 'required_format': 'Date'},
# #         'PO_DELIVERY_ADDRESS': {'location': (0.06, 0.19, 0.42, 0.23), 'required_format': 'String'}
# #     }
# # ]

# # def extract_text_from_bbox(label, image, bbox):
# #     location_points = bbox['location']
# #     key = bbox['key']
# #     required_format = bbox['required_format']

# #     img_width, img_height = image.size

# #     left = location_points[0] * img_width
# #     top = location_points[1] * img_height
# #     right = location_points[2] * img_width
# #     bottom = location_points[3] * img_height

# #     cropped_image = image.crop((left, top, right, bottom))
# #     filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{label}.png"
# #     cropped_image.save(os.path.join('processed', filename), required_format='PNG')

# #     text = pytesseract.image_to_string(cropped_image)
# #     if bbox['required_format'] == 'Date':
# #         text = correct_date_format(text)

# #     read_text = text.strip()
# #     return read_text

# # def correct_date_format(date_str):
# #     date_str = date_str.replace('/', '')

# #     day = date_str[:2]
# #     month = date_str[2:4]
# #     year = date_str[4:]

# #     if len(year) == 2:
# #         year = f"20{year}"
# #     elif len(year) == 4 and int(year[:2]) == 0:
# #         year = f"20{year[-2:]}"

# #     corrected_date_str = f"{day}/{month}/{year}"

# #     return corrected_date_str

# # def resize_image(image):
# #     width = 600
# #     height = 600
# #     resized_img = image.resize((width, height))
# #     return resized_img