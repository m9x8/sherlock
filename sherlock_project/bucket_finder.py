import asyncio
from typing import List, Dict, Tuple
from sherlock_project.stealth_engine import StealthEngine

class BucketFinder:
    def __init__(self, stealth_engine: StealthEngine):
        self.stealth_engine = stealth_engine

    def _generate_permutations(self, base_word: str) -> List[str]:
        # Simple permutations for bucket names
        suffixes = ['-assets', '-public', '-backup', '-dev', '-prod', '-staging', '-test', '-media']
        prefixes = ['assets-', 'backup-', 'dev-', 'prod-', 'staging-']

        perms = [base_word]
        for s in suffixes:
            perms.append(f"{base_word}{s}")
        for p in prefixes:
            perms.append(f"{p}{base_word}")

        return perms

    async def _check_bucket(self, url: str) -> Tuple[str, int]:
        """
        Performs a HEAD request.
        Returns URL and status code.
        """
        try:
            # We don't want to follow redirects for bucket discovery usually,
            # and HEAD is faster.
            response = await self.stealth_engine.request('HEAD', url, allow_redirects=False)
            return url, response.status_code
        except Exception:
            return url, 0

    async def scan_buckets(self, base_name: str) -> Dict[str, Dict[str, str]]:
        """
        Scans for AWS S3, GCP, and Azure Blob storage buckets.
        Returns a dictionary mapping cloud provider to found bucket URLs and their status.
        Status 200 = Publicly accessible (potentially)
        Status 403 = Exists but private
        Status 404 = Doesn't exist
        """
        permutations = self._generate_permutations(base_name)

        aws_urls = [f"https://{p}.s3.amazonaws.com" for p in permutations]
        gcp_urls = [f"https://storage.googleapis.com/{p}" for p in permutations]
        # Azure blob usually requires a known storage account name. We guess the account name here.
        azure_urls = [f"https://{p}.blob.core.windows.net" for p in permutations]

        all_urls = aws_urls + gcp_urls + azure_urls

        tasks = [self._check_bucket(url) for url in all_urls]
        results = await asyncio.gather(*tasks)

        findings = {
            "aws": {},
            "gcp": {},
            "azure": {}
        }

        for url, status in results:
            if status in [200, 403]: # We care if it exists (200 or 403)
                status_str = "Public" if status == 200 else "Private/Access Denied"
                if ".s3.amazonaws.com" in url:
                    findings["aws"][url] = status_str
                elif "storage.googleapis.com" in url:
                    findings["gcp"][url] = status_str
                elif ".blob.core.windows.net" in url:
                    findings["azure"][url] = status_str

        return findings
