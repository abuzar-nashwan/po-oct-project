# import fitz
# import re

# def extract_text_from_pdf(pdf_path):
#     document = fitz.open(pdf_path)
#     text = ""
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         text += page.get_text()

#     return text

# def parse_order_details(text):
#     order_details = {}

#     order_number_pattern = r"Order Number\s*:\s*(\d+)"
#     delivery_date_pattern = r"Delivery Date\s*:\s*(\d{2}/\d{2}/\d{4})"
#     ship_to_pattern = r"Ship To\s*:\s*([^:]+)"

#     order_number_match = re.search(order_number_pattern, text)
#     delivery_date_match = re.search(delivery_date_pattern, text)
#     ship_to_match = re.search(ship_to_pattern, text)

#     if order_number_match:
#         order_details['Order Number'] = order_number_match.group(1)
#     if delivery_date_match:
#         order_details['Delivery Date'] = delivery_date_match.group(1)
#     if ship_to_match:
#         order_details['Ship To'] = ship_to_match.group(1).strip()

#     return order_details


# pdf_path = '/Users/sivvi/Documents/repos/tesseract-exp/ocr_project/04-06-202414_39_00_506510C11550 (1).pdf'
# pdf_text = extract_text_from_pdf(pdf_path)
# order_details = parse_order_details(pdf_text)

# print("Extracted Order Details:")
# print(order_details)

# def extract_text_with_bbox(pdf_path):
#     document = fitz.open(pdf_path)
#     text_with_bbox = []

#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if "lines" in block:
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         bbox = span["bbox"]
#                         text = span["text"]
#                         text_with_bbox.append((text, bbox))

#     return text_with_bbox

# def find_text_with_bb(key, text_with_bbox, boundary=0):
#     ship_to_address = ""
#     ship_to_bbox = None

#     for text, bbox in text_with_bbox:
#         if key in text:
#             ship_to_bbox = bbox
#             break

#     if ship_to_bbox:
#         x0, y0, x1, y1 = ship_to_bbox
#         y_boundary = y1 + boundary

#         for text, bbox in text_with_bbox:
#             tx0, ty0, tx1, ty1 = bbox
#             if ty0 > y1 and ty0 <= y_boundary:
#                 ship_to_address += " " + text

#     return ship_to_address.strip()

# pdf_path = '/Users/sivvi/Documents/repos/tesseract-exp/ocr_project/04-06-202414_39_00_506510C11550 (1).pdf'
# text_with_bbox = extract_text_with_bbox(pdf_path)

# ship_to_address = find_text_with_bb('Ship To', text_with_bbox, boundary=5)


# print("Ship To: ", ship_to_address)

