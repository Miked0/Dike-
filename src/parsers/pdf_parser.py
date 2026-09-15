"""
PDF parser for extracting text from PDF files.
Supports both text-based PDFs and scanned PDFs (via OCR).
"""
import logging
from typing import Union
import io

# Try to import necessary libraries, with fallbacks
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

try:
    from PIL import Image
except ImportError:
    Image = None

# Import our OCR utility
try:
    from src.utils.ocr import ocr_from_image
except ImportError:
    # Fallback if the utility is not available (should not happen in the project)
    def ocr_from_image(image):
        raise ImportError("OCR utility not available")

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_content: Union[bytes, io.BytesIO]) -> str:
    """
    Extract text from a PDF file.
    First attempts to extract text directly (for text-based PDFs).
    If that fails or yields little text, falls back to OCR (for scanned PDFs).

    Args:
        file_content: The PDF file content as bytes or a BytesIO object.

    Returns:
        Extracted text as a string. Returns empty string if extraction fails.
    """
    # Ensure we have bytes
    if isinstance(file_content, io.BytesIO):
        pdf_bytes = file_content.getvalue()
    elif isinstance(file_content, bytes):
        pdf_bytes = file_content
    else:
        raise TypeError("file_content must be bytes or io.BytesIO")

    # First, try text extraction with PyPDF2
    text = ""
    if PyPDF2 is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            logger.warning(f"PyPDF2 text extraction failed: {e}")
            text = ""

    # If we got a reasonable amount of text, return it
    # Threshold: 50 characters (adjust as needed)
    if text.strip() and len(text.strip()) >= 50:
        logger.info(f"Extracted {len(text)} characters via PyPDF2")
        return text.strip()

    # Otherwise, fall back to OCR
    logger.info("Falling back to OCR for PDF text extraction")
    if convert_from_bytes is None or Image is None:
        logger.error("OCR dependencies (pdf2image, Pillow) not installed")
        return ""

    try:
        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes)
        if not images:
            logger.warning("No images generated from PDF")
            return ""

        # Extract text from each image using OCR
        ocr_texts = []
        for i, image in enumerate(images):
            try:
                page_text = ocr_from_image(image)
                if page_text:
                    ocr_texts.append(page_text)
                    logger.debug(f"OCR on page {i+1} yielded {len(page_text)} characters")
            except Exception as e:
                logger.warning(f"OCR failed on page {i+1}: {e}")

        combined_text = "\n".join(ocr_texts)
        logger.info(f"Extracted {len(combined_text)} characters via OCR")
        return combined_text.strip()

    except Exception as e:
        logger.error(f"OCR process failed: {e}")
        return ""