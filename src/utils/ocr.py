"""
OCR utility for extracting text from images using Tesseract.
"""
import logging
from typing import Union
import io

# Try to import necessary libraries, with fallbacks
try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)

def ocr_from_image(image: Union[Image.Image, bytes, io.BytesIO]) -> str:
    """
    Extract text from an image using OCR (Tesseract).

    Args:
        image: PIL Image object, bytes, or BytesIO containing image data

    Returns:
        Extracted text as a string. Returns empty string if OCR fails.
    """
    if pytesseract is None or Image is None:
        logger.error("OCR dependencies (pytesseract, Pillow) not installed")
        return ""

    try:
        # Convert input to PIL Image if needed
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        elif isinstance(image, io.BytesIO):
            image = Image.open(image)
        # If it's already a PIL Image, use as-is

        # Perform OCR
        text = pytesseract.image_to_string(image, lang='por')  # Portuguese language
        return text.strip()

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

def ocr_from_file(file_path: str) -> str:
    """
    Extract text from an image file using OCR (Tesseract).

    Args:
        file_path: Path to the image file

    Returns:
        Extracted text as a string. Returns empty string if OCR fails.
    """
    if pytesseract is None or Image is None:
        logger.error("OCR dependencies (pytesseract, Pillow) not installed")
        return ""

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='por')  # Portuguese language
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed for file {file_path}: {e}")
        return ""