# PDF Test Files for CT-008

To properly test CT-008 (Validação com PDF de Cupom Fiscal), you need to create:

1. A valid PDF file containing a readable cupom fiscal with the data specified in pdf_test_spec.json
2. Optionally, a corrupted PDF file to test error handling
3. Optionally, a PDF with different layouts to test robustness

The PDF should contain text that can be extracted by the PDF parser (src/parsers/pdf_parser.py).
For scanned PDFs, ensure the OCR functionality (src/utils/ocr.py) can extract the text properly.

See pdf_test_spec.json for the expected data that should be extracted.
