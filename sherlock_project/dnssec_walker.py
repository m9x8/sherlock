import dns.resolver
import dns.message
import dns.query
import dns.rdatatype
import dns.name
from typing import List, Optional, Set

class DNSSECWalker:
    def __init__(self, nameservers: Optional[List[str]] = None):
        self.resolver = dns.resolver.Resolver()
        if nameservers:
            self.resolver.nameservers = nameservers
        else:
            # Use public resolvers by default
            self.resolver.nameservers = ['8.8.8.8', '1.1.1.1']

    def walk_domain(self, domain: str) -> Set[str]:
        """
        Attempts to perform NSEC walking on a domain to find subdomains.
        """
        found_subdomains: Set[str] = set()

        try:
            # Get authoritative nameservers for the domain
            ns_answers = self.resolver.resolve(domain, 'NS')
            auth_ns_list = [ns.to_text() for ns in ns_answers]

            if not auth_ns_list:
                return found_subdomains

            auth_ns = auth_ns_list[0]
            ns_ip = self.resolver.resolve(auth_ns, 'A')[0].to_text()

            # Start walking from the apex
            current_name = domain
            visited = set()

            while True:
                # Query for a non-existent subdomain strictly before the current name to trigger NSEC
                # By querying for '0' prepended, we ask for something that comes before the current name in canonical order
                # However, to actually walk the chain forward, we query for the current name but ask for a type that doesn't exist
                # If we want the next record, we can query for a non-existent type at current_name
                request = dns.message.make_query(current_name, dns.rdatatype.TYPE65534)
                request.want_dnssec(True)

                try:
                    response = dns.query.udp(request, ns_ip, timeout=5)
                except Exception:
                    break

                next_name = None

                for rrset in response.answer + response.authority:
                    if rrset.rdtype == dns.rdatatype.NSEC:
                        for rr in rrset:
                            nxt = rr.next.to_text()
                            if nxt.endswith(f".{domain}.") or nxt == f"{domain}.":
                                clean_name = nxt.rstrip('.')
                                found_subdomains.add(clean_name)
                                next_name = clean_name
                                break
                    if next_name:
                        break

                if not next_name or next_name in visited or next_name == domain:
                    break

                visited.add(next_name)
                current_name = next_name

        except Exception as e:
            pass

        return found_subdomains
