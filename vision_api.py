import io
import re
import sys
import ngram
from xlwt import Workbook
from pdf2image import convert_from_path
from google.cloud import vision

from constants import KEYS
from settings import get_env_var

# get google application credentials from .env file
GOOGLE_APPLICATION_CREDENTIALS = get_env_var("GOOGLE_APPLICATION_CREDENTIALS")

try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    print("unable to create vision client", e)

# Method to match texts with keys texts and regex
def get_value(k, full_text):
    for i, text in enumerate(full_text):
        if ngram.NGram.compare(text, k["text"], N=1) > 0.8:
            for j in range(i + 1, len(full_text)):
                match = re.search(k["regex"], full_text[j])

                if match:
                    return match.group(0)
    return ""


def create_image_and_extract_data(pdf_file):
    """
    Take pdf file path from command line argument and convert into jpg files
    and pass it to the google vision APIs to perform OCR
    :param pdf_file: pdf file path
    :return: res
    """
    pages = convert_from_path(pdf_file)
    index = 1

    for page in pages:
        filepath = f"ocr_page_{index}.jpg"
        page.save(filepath)
        index += 1

        with io.open(filepath, 'rb') as img:
            content = img.read()
        try:
            image = vision.Image(content=content)
        except Exception as e:
            print("Excception on creating Image object", e)
        try:
            response = client.text_detection(image=image)
        except Exception as e:
            print("Exception while detecting text", e)
        full_text = response.text_annotations
        full_text = full_text[0].description.split('\n')

        # list to store matched text
        res = []

        for k in KEYS:
            res.append(get_value(k, full_text))

        return res


def create_xls_file(result):
    """
    Method to create xls file and store data into it
    :param result: list containing extracted data
    :return: create xls output file
    """
    # Workbook is created
    wb = Workbook()

    # add_sheet is used to create sheet.
    sheet = wb.add_sheet('Vision')
    sheet.write(0, 0, 'Address')
    sheet.write(0, 1, 'Id')
    sheet.write(1, 0, result[0])
    sheet.write(1, 1, result[1])
    wb.save('./Output/ocr.xls')


# read file path from command line argument
pdf_file = sys.argv[1]
result = create_image_and_extract_data(pdf_file)
create_xls_file(result)
print(result)
