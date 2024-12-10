import fitz  # PyMuPDF

def extract_pdf_style(file_path, page_num=0):
    document = fitz.open(file_path)
    styles = []

    page = document.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    style = {
                        "font": span["font"],
                        "size": span["size"],
                        "color": span["color"],
                        "bbox": span["bbox"]
                    }
                    styles.append(style)
    return styles


def compare_styles(styles1, styles2):
    # if len(styles1) != len(styles2):
    #     return False, 0
    
    differences = []
    for s1, s2 in zip(styles1, styles2):
        if s1 != s2:
            differences.append((s1, s2))

    similarity_ratio = (len(styles1) - len(differences)) / len(styles1)
    return similarity_ratio, differences

def show_differences(differences):
    for diff in differences:
        s1, s2 = diff
        print("Difference found:")
        print("Style 1:", s1)
        print("Style 2:", s2)
        print()

file1 ='/Users/sivvi/Documents/repos/tesseract-exp/ocr_project/Test 1.pdf'
file2 = '/Users/sivvi/Documents/repos/tesseract-exp/ocr_project/Test 2.pdf'

# Extract styles from both PDFs
styles1 = extract_pdf_style(file1, page_num=0)
styles2 = extract_pdf_style(file2, page_num=0)


# Compare the styles
similarity_ratio, differences = compare_styles(styles1, styles2)

def write_differences_to_file(differences, file_path):
    with open(file_path, 'w') as file:
        for diff in differences:
            s1, s2 = diff
            file.write("Difference found:\n")
            file.write(f"Style 1: {s1}\n")
            file.write(f"Style 2: {s2}\n")
            file.write("\n")


output_file = "differences_output.txt"
with open(output_file, 'w') as file:
    if similarity_ratio < 0.5:
        file.write("The PDFs do not have the same format and style.\n")
        file.write(f"Similarity ratio: {similarity_ratio*100:.2f}%\n")
        write_differences_to_file(differences, output_file)
    else:
        file.write("The PDFs have a similar format and style.\n")
        file.write(f"Similarity ratio: {similarity_ratio*100:.2f}%\n")



