import ssl
import socket
from typing import List, Optional, Tuple, Set
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class KeyCorrelator:
    @staticmethod
    def get_ssl_san(hostname: str, port: int = 443, timeout: float = 3.0) -> List[str]:
        """
        Extracts Subject Alternative Names (SAN) from a server's SSL certificate.
        """
        sans: Set[str] = set()
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    if cert_der:
                        cert = x509.load_der_x509_certificate(cert_der, default_backend())
                        try:
                            ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                            sans.update(ext.value.get_values_for_type(x509.DNSName))
                        except x509.ExtensionNotFound:
                            pass
        except Exception:
            pass

        return list(sans)

    @staticmethod
    def get_ssh_banner(hostname: str, port: int = 22, timeout: float = 3.0) -> Optional[str]:
        """
        Basic SSH banner grabbing.
        """
        try:
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                # Read banner (typically first line ending in \n)
                data = sock.recv(1024)
                if data:
                    banner = data.decode('utf-8', errors='ignore').strip()
                    if banner.startswith("SSH-"):
                        return banner
        except Exception:
            pass
        return None
