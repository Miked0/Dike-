# OCR Validation Script Template
import pytesseract
from PIL import Image
import sys
from difflib import SequenceMatcher

def validate_ocr(image_path, expected_text, threshold=0.8):
    """
    Validate OCR output against expected text.
    Args:
        image_path: Path to the image file.
        expected_text: The expected text string.
        threshold: Minimum similarity ratio to consider a match (0.0 to 1.0).
    Returns:
        True if OCR output is similar enough to expected text, False otherwise.
    """
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        similarity = SequenceMatcher(None, text, expected_text).ratio()
        return similarity >= threshold
    except Exception as e:
        print(f"Error during OCR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python validation_script.py <image_path> <expected_text>")
        sys.exit(1)
    image_path = sys.argv[1]
    expected_text = sys.argv[2]
    if validate_ocr(image_path, expected_text):
        print("OCR validation passed.")
        sys.exit(0)
    else:
        print("OCR validation failed.")
        sys.exit(1)