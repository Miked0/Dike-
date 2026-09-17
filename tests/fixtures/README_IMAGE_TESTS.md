# Image Test Files for CT-009

To properly test CT-009 (Validação com Imagem de Cupom Fiscal), you need to create:

1. A valid image file (JPEG/PNG) containing a readable cupom fiscal with the data specified in image_test_spec.json
2. Optionally, corrupted image files to test error handling
3. Optionally, images with different qualities, rotations, lighting conditions to test OCR robustness

The image should be clear enough for OCR to extract the text properly.
See image_test_spec.json for the expected data that should be extracted via OCR.
