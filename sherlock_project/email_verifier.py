import dns.resolver
from typing import Tuple, List

class EmailVerifier:
    def __init__(self):
        # A small sample list of common disposable email domains
        # In a real-world scenario, this would be loaded from a larger, updated file or source.
        self.dea_domains = {
            "mailinator.com", "guerrillamail.com", "10minutemail.com",
            "temp-mail.org", "yopmail.com", "sharklasers.com"
        }
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = ['8.8.8.8', '1.1.1.1']

    def is_disposable(self, email: str) -> bool:
        """
        Basic check against a known list of disposable email address (DEA) domains.
        """
        if "@" not in email:
            return False
        domain = email.split("@")[1].lower()
        return domain in self.dea_domains

    def verify_mx(self, email: str) -> Tuple[bool, List[str]]:
        """
        Passively verifies if the domain of the email has valid MX records.
        Returns a tuple: (has_mx_records, list_of_mx_servers)
        """
        if "@" not in email:
            return False, []

        domain = email.split("@")[1].lower()
        mx_servers = []

        try:
            answers = self.resolver.resolve(domain, 'MX')
            for rdata in answers:
                mx_servers.append(rdata.exchange.to_text().rstrip('.'))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            pass

        return len(mx_servers) > 0, mx_servers
