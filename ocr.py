
import numpy as np
from PIL import Image
import pytesseract
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OCR:
    def __init__(self):
        # PSM6 = "assume single uniform block of text"
        self.config = "--psm 6"

    def extract(self, frame):
        
        # returns empty string if cant detect anyth
        
        
        img = Image.fromarray(frame)

        
        img = img.convert("L") #convert to b/w

        # lighter pixels -> white
        # darker pixels -> black
        img = img.point(lambda x: 0 if x < 140 else 255, "1")

        # run tesseract
        text = pytesseract.image_to_string(img, config=self.config)

        return text.strip()
