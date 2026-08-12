import mmh3
import codecs
import base64
from typing import Optional

class FaviconHasher:
    @staticmethod
    def hash_favicon_bytes(favicon_bytes: bytes) -> Optional[int]:
        """
        Calculates the MurmurHash3 (MMH3) hash of the base64-encoded favicon bytes,
        similarly to Shodan.
        """
        if not favicon_bytes:
            return None

        try:
            # Base64 encode the bytes and format them as Shodan does
            # Shodan requires inserting newlines every 76 characters
            encoded = base64.b64encode(favicon_bytes)
            # Add newlines every 76 chars
            formatted_encoded = b""
            for i in range(0, len(encoded), 76):
                formatted_encoded += encoded[i:i+76] + b"\n"

            # Calculate mmh3 hash using the formatted base64 string
            return mmh3.hash(formatted_encoded)
        except Exception:
            return None
