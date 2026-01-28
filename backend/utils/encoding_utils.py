"""
Encoding detection and conversion utilities
"""

from typing import Optional, Tuple

import chardet


def detect_encoding(content: bytes) -> Tuple[str, float]:
    """Detect the encoding of byte content

    Returns:
        Tuple of (encoding_name, confidence)
    """
    result = chardet.detect(content)
    encoding = result.get("encoding", "utf-8") or "utf-8"
    confidence = result.get("confidence", 0.0) or 0.0

    # Normalize encoding names
    encoding_map = {
        "gb2312": "gbk",
        "gb18030": "gbk",
        "ascii": "utf-8",
    }

    encoding = encoding.lower()
    encoding = encoding_map.get(encoding, encoding)

    return encoding, confidence


def decode_content(content: bytes, encoding: Optional[str] = None) -> str:
    """Decode byte content to string with fallback encodings

    Args:
        content: Byte content to decode
        encoding: Optional encoding to try first

    Returns:
        Decoded string
    """
    # Encodings to try in order
    encodings_to_try = []

    if encoding:
        encodings_to_try.append(encoding)

    # Detect encoding
    detected, confidence = detect_encoding(content)
    if detected and detected not in encodings_to_try:
        encodings_to_try.append(detected)

    # Common fallback encodings
    fallbacks = ["utf-8", "gbk", "gb18030", "big5", "latin-1"]
    for enc in fallbacks:
        if enc not in encodings_to_try:
            encodings_to_try.append(enc)

    # Try each encoding
    for enc in encodings_to_try:
        try:
            return content.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue

    # Last resort: decode with errors='ignore'
    return content.decode("utf-8", errors="ignore")


def encode_content(text: str, encoding: str = "utf-8") -> bytes:
    """Encode string to bytes with fallback

    Args:
        text: String to encode
        encoding: Target encoding

    Returns:
        Encoded bytes
    """
    try:
        return text.encode(encoding)
    except UnicodeEncodeError:
        # Replace unencodable characters
        return text.encode(encoding, errors="replace")


def convert_encoding(content: bytes, target_encoding: str = "utf-8") -> bytes:
    """Convert content from one encoding to another

    Args:
        content: Byte content to convert
        target_encoding: Target encoding (default utf-8)

    Returns:
        Converted bytes
    """
    # First decode
    text = decode_content(content)

    # Then encode to target
    return encode_content(text, target_encoding)


def is_utf8(content: bytes) -> bool:
    """Check if content is valid UTF-8"""
    try:
        content.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def remove_bom(content: bytes) -> bytes:
    """Remove BOM (Byte Order Mark) from content"""
    boms = [
        (b"\xef\xbb\xbf", "utf-8-sig"),  # UTF-8 BOM
        (b"\xff\xfe", "utf-16-le"),  # UTF-16 LE BOM
        (b"\xfe\xff", "utf-16-be"),  # UTF-16 BE BOM
        (b"\xff\xfe\x00\x00", "utf-32-le"),  # UTF-32 LE BOM
        (b"\x00\x00\xfe\xff", "utf-32-be"),  # UTF-32 BE BOM
    ]

    for bom, _ in boms:
        if content.startswith(bom):
            return content[len(bom) :]

    return content


def normalize_line_endings(text: str) -> str:
    """Normalize line endings to Unix style (LF)"""
    # Convert Windows (CRLF) and old Mac (CR) to Unix (LF)
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text
