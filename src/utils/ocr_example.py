"""
Example demonstrating how to use the OCR utility for PDF and image processing.
This is intended as documentation/example for developers implementing task 5.
"""

from src.utils.ocr import ocr_from_image, ocr_from_file
from src.parsers.pdf_parser import extract_text_from_pdf
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_cuf_fiscal_pdf(file_content: bytes) -> str:
    """
    Process a fiscal coupon PDF file and extract text.
    This demonstrates how the OCR utility is used by the PDF parser.

    Args:
        file_content: The PDF file content as bytes

    Returns:
        Extracted text as string
    """
    logger.info("Processing fiscal coupon PDF...")

    # Use the existing PDF parser which already has OCR fallback built-in
    extracted_text = extract_text_from_pdf(file_content)

    if extracted_text:
        logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
        return extracted_text
    else:
        logger.warning("Failed to extract text from PDF")
        return ""

def process_cuf_fiscal_image(image_content: bytes) -> str:
    """
    Process a fiscal coupon image file and extract text using OCR.

    Args:
        image_content: The image file content as bytes

    Returns:
        Extracted text as string
    """
    logger.info("Processing fiscal coupon image with OCR...")

    # Use the OCR utility directly
    extracted_text = ocr_from_image(image_content)

    if extracted_text:
        logger.info(f"Successfully extracted {len(extracted_text)} characters from image via OCR")
        return extracted_text
    else:
        logger.warning("Failed to extract text from image via OCR")
        return ""

def process_cuf_fiscal_image_from_file(file_path: str) -> str:
    """
    Process a fiscal coupon image from file path and extract text using OCR.

    Args:
        file_path: Path to the image file

    Returns:
        Extracted text as string
    """
    logger.info(f"Processing fiscal coupon image from file: {file_path}")

    # Use the OCR utility with file path
    extracted_text = ocr_from_file(file_path)

    if extracted_text:
        logger.info(f"Successfully extracted {len(extracted_text)} characters from image file via OCR")
        return extracted_text
    else:
        logger.warning(f"Failed to extract text from image file {file_path} via OCR")
        return ""

# Example usage:
if __name__ == "__main__":
    # This is just an example of how it would be used
    # In practice, these functions would be called from your validation/service layer

    # Example with PDF
    # with open("sample_cupom.pdf", "rb") as f:
    #     pdf_content = f.read()
    #     text = process_cuf_fiscal_pdf(pdf_content)
    #     print(f"Extracted text: {text[:200]}...")

    # Example with image
    # with open("sample_cupom.jpg", "rb") as f:
    #     image_content = f.read()
    #     text = process_cuf_fiscal_image(image_content)
    #     print(f"Extracted text: {text[:200]}...")

    # Example with image file path
    # text = process_cuf_fiscal_image_from_file("sample_cupom.png")
    # print(f"Extracted text: {text[:200]}...")
    pass