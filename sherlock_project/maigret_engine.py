import asyncio
from typing import Dict, List, Any, Optional
import maigret
import os
import logging
import sys

# Provide a mock that acts like a file descriptor
class DummyStream:
    def write(self, *args, **kwargs):
        pass
    def flush(self, *args, **kwargs):
        pass
    def isatty(self):
        return False
    def fileno(self):
        # /dev/null
        return os.open(os.devnull, os.O_RDWR)

class MaigretEngine:
    def __init__(self, logger=None, stealth_engine=None):
        self.logger = logger or logging.getLogger('maigret_engine')
        self.stealth = stealth_engine
        self.db = None

    def setup_db(self):
        if self.db is None:
            db_file = os.path.join(os.path.dirname(maigret.__file__), 'resources', 'data.json')
            self.db = maigret.MaigretDatabase().load_from_path(db_file)
        return self.db

    async def search(self, username: str, timeout: int = 10, proxy: str = None, top: int = 100) -> List[Dict[str, Any]]:
        db = self.setup_db()
        sites = db.ranked_sites_dict(top=top)

        sites_to_check = {
            site_name: site
            for site_name, site in sites.items()
            if not site.disabled
        }

        results = []

        # Override stdout to hide progress bar
        old_stdout = sys.stdout
        sys.stdout = DummyStream()

        try:
            logger = logging.getLogger('maigret')
            logger.setLevel(logging.CRITICAL)

            # maigret search uses a progressbar internally
            results_dict = await maigret.search(
                username=username,
                site_dict=sites_to_check,
                timeout=timeout,
                logger=logger,
                max_connections=50,
                no_progress=True,
                proxy=proxy
            )

            for site_name, site_result in results_dict.items():
                status = site_result.get('status')

                is_claimed = False

                if hasattr(status, 'name') and status.name == 'CLAIMED':
                    is_claimed = True
                elif hasattr(status, 'value') and str(status.value).upper() == 'CLAIMED':
                    is_claimed = True
                elif str(status).upper() == 'CLAIMED' or 'CLAIMED' in str(status).upper():
                    is_claimed = True

                if is_claimed:
                    results.append({
                        "site": site_name,
                        "url_user": site_result.get('url_user'),
                        "is_valid": True,
                        "tags": site_result.get('site').tags if hasattr(site_result.get('site'), 'tags') else [],
                        "data": site_result.get('tags', {})
                    })

        except Exception as e:
            if self.logger:
                self.logger.error(f"Maigret search failed: {e}")
            else:
                print(f"Maigret search failed: {e}", file=sys.stderr)
        finally:
            sys.stdout = old_stdout

        return results
