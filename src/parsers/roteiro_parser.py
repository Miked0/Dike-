"""
Parser for test script files (CSV/XLSX).
Supports both CSV and Excel formats for test case definitions.
"""
import logging
from typing import Union, List, Dict, Any
import io

# Try to import necessary libraries
try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

def parse_test_script(file_content: Union[bytes, io.BytesIO], file_type: str) -> List[Dict[str, Any]]:
    """
    Parse test script file (CSV or XLSX) and extract test cases.

    Args:
        file_content: The file content as bytes or BytesIO
        file_type: Either 'csv' or 'xlsx' to determine parsing method

    Returns:
        List of dictionaries representing test cases
    """
    if pd is None:
        logger.error("Pandas not installed. Cannot parse CSV/XLSX files.")
        return []

    # Ensure we have bytes
    if isinstance(file_content, io.BytesIO):
        content_bytes = file_content.getvalue()
    elif isinstance(file_content, bytes):
        content_bytes = file_content
    else:
        raise TypeError("file_content must be bytes or io.BytesIO")

    try:
        # Create BytesIO object for pandas
        bytes_io = io.BytesIO(content_bytes)

        # Parse based on file type
        if file_type.lower() == 'csv':
            df = pd.read_csv(bytes_io)
        elif file_type.lower() in ['xlsx', 'excel']:
            df = pd.read_excel(bytes_io)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return []

        # Convert DataFrame to list of dictionaries
        test_cases = df.to_dict('records')

        logger.info(f"Parsed {len(test_cases)} test cases from {file_type.upper()} file")
        return test_cases

    except Exception as e:
        logger.error(f"Failed to parse {file_type} file: {e}")
        return []