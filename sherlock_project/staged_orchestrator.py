"""
Staged Orchestrator Module
Central orchestrator to handle all reconnaissance through a standard pipeline:
STAGE 0 - Normalize
STAGE 1 - Authoritative direct sources
STAGE 2 - Stealth SERP fallback
STAGE 3 - Conditional pivots
STAGE 4 - Fusion + confidence
STAGE 5 - Ranked output
"""

import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class StagedOrchestrator:
    def __init__(self, ui_callback_msg, ui_callback_progress, ui_callback_result):
        self.ui_callback_msg = ui_callback_msg
        self.ui_callback_progress = ui_callback_progress
        self.ui_callback_result = ui_callback_result
        self.semaphore = asyncio.Semaphore(4)  # Bounded concurrency
        self.results_cache = []

    async def run_search(self, target_type: str, target: Any, stop_event=None) -> List[Dict[str, Any]]:
        """
        Runs the full 5-stage OSINT pipeline.
        target_type: 'company', 'person', 'phone', 'email', 'username', 'domain'
        """
        try:
            # STAGE 0: Normalize & Variant Expansion
            self.post_message(f"--- STAGE 0: Normalizing {target_type} target ---")
            variants = await self._run_stage_0_normalize(target_type, target)
            self.post_progress(1, 5)

            if stop_event and stop_event.is_set():
                return []

            # STAGE 1: Authoritative sources
            self.post_message(f"--- STAGE 1: Authoritative Sources ---")
            stage1_results = await self._run_stage_1_authoritative(target_type, variants, stop_event)
            self.post_progress(2, 5)

            if stop_event and stop_event.is_set():
                return []

            # STAGE 2: Stealth SERP
            self.post_message(f"--- STAGE 2: Stealth SERP Fallback ---")
            stage2_results = await self._run_stage_2_serp(target_type, variants, stage1_results, stop_event)
            self.post_progress(3, 5)

            if stop_event and stop_event.is_set():
                return []

            # STAGE 3: Conditional Pivots
            self.post_message(f"--- STAGE 3: Conditional Pivots ---")
            stage3_results = await self._run_stage_3_pivots(target_type, stage1_results + stage2_results, stop_event)
            self.post_progress(4, 5)

            if stop_event and stop_event.is_set():
                return []

            # STAGE 4: Fusion + Confidence
            self.post_message(f"--- STAGE 4: Fusion & Confidence Scoring ---")
            raw_results = stage1_results + stage2_results + stage3_results
            fused_results = await self._run_stage_4_fusion(raw_results)
            self.post_progress(5, 5)

            # STAGE 5: Ranked Output (Return sorted)
            return self._run_stage_5_ranking(fused_results)

        except Exception as e:
            logger.error(f"Error in StagedOrchestrator pipeline: {e}")
            self.post_message(f"Pipeline error: {e}")
            return []

    async def _run_stage_0_normalize(self, target_type: str, target: Any) -> Dict[str, Any]:
        """
        Builds a ranked variant set per target type.
        """
        variants = {"original": target, "expanded": []}

        if target_type == "company":
            import re
            name = target.strip()
            variants["expanded"].append(name)
            # Without legal form
            clean_name = re.sub(r'(?i)\b(B\.?V\.?|N\.?V\.?|Ltd\.?|Inc\.?|GmbH|LLC)\b', '', name).strip()
            if clean_name and clean_name != name:
                variants["expanded"].append(clean_name)
            # Remove spaces
            no_spaces = name.replace(" ", "")
            if no_spaces != name:
                variants["expanded"].append(no_spaces)

        elif target_type == "person":
            first, last, extra = target
            variants["expanded"].append(f"{first} {last}")
            variants["expanded"].append(f"{last}, {first}")
            if len(first) > 0:
                variants["expanded"].append(f"{first[0]}. {last}")

        elif target_type == "phone":
            from sherlock_project.phone_search import PhoneOSINT
            import re
            po = PhoneOSINT()
            meta = po.validate_and_meta(target)
            if meta.get("valid"):
                variants["expanded"].append(meta["e164"])
                variants["expanded"].append(meta["national"])
                variants["expanded"].append(meta["international"])
                clean_national = re.sub(r"[^\d]", "", meta["national"])
                if clean_national:
                    variants["expanded"].append(clean_national)
            else:
                variants["expanded"].append(target)
            variants["meta"] = meta

        elif target_type in ["email", "username"]:
            variants["expanded"].append(target)

        elif target_type == "domain":
            variants["expanded"].append(target)

        return variants

    async def _run_stage_1_authoritative(self, target_type: str, variants: Dict[str, Any], stop_event) -> List[Dict[str, Any]]:
        results = []
        tasks = []

        async def _safe_run(coro):
            async with self.semaphore:
                try:
                    return await coro
                except Exception as e:
                    logger.error(f"Authoritative source failed: {e}")
                    return []

        if target_type == "phone":
            from sherlock_project.scraper import HighEndScraper
            meta = variants.get("meta", {})
            if meta and meta.get("valid"):
                clean_num = meta.get("national", variants["original"])
                async def _scrape_phone():
                    async with HighEndScraper(timeout=20) as scraper:
                        hits = await scraper.scrape_phone_nl_registries(clean_num)
                        return [{
                            "title": h["title"], "url": h["url"], "snippet": h["snippet"],
                            "source_tool": "tellows/wieheeftgebeld", "source_type": "direct",
                            "confidence": "high", "entity_type": "phone"
                        } for h in hits]
                tasks.append(_safe_run(_scrape_phone()))

        elif target_type == "company":
            from sherlock_project.scraper import HighEndScraper
            company_name = variants["original"]
            async def _scrape_company():
                async with HighEndScraper(timeout=20) as scraper:
                    hits = await scraper.scrape_company_direct_details(company_name)
                    return [{
                        "title": h["title"], "url": h["url"], "snippet": h["snippet"],
                        "source_tool": "openkvk", "source_type": "registry",
                        "confidence": "high", "entity_type": "company"
                    } for h in hits]
            tasks.append(_safe_run(_scrape_company()))

        elif target_type == "email":
            email = variants["original"]
            async def _run_holehe():
                import subprocess
                import json
                try:
                    # Run holehe in a separate subprocess to avoid event loop conflicts, passing only top domains for speed or relying on its default output.
                    # As holehe outputs directly to stdout, we use --only-used if available or parse standard output.
                    proc = await asyncio.create_subprocess_exec(
                        "holehe", email, "--only-used", "--no-color",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, _ = await proc.communicate()
                    hits = []
                    # Basic parser: look for [+]
                    for line in stdout.decode().splitlines():
                        if "[+]" in line:
                            site = line.split("[+]")[1].strip()
                            hits.append({
                                "title": f"Account found on {site}", "url": f"https://{site}", "snippet": f"Email {email} is registered on {site}",
                                "source_tool": "holehe", "source_type": "account_enum",
                                "confidence": "high", "entity_type": "email"
                            })
                    return hits
                except Exception as e:
                    logger.error(f"Holehe execution failed: {e}")
                    return []
            tasks.append(_safe_run(_run_holehe()))

        elif target_type == "username":
            username = variants["original"]
            async def _run_maigret():
                from sherlock_project.maigret_engine import MaigretEngine
                engine = MaigretEngine()
                hits = await engine.search(username, timeout=10, top=100)
                return [{
                    "title": h.get("site", "Unknown Site"), "url": h.get("url", ""),
                    "snippet": f"Username {username} found on {h.get('site', '')}",
                    "source_tool": "maigret", "source_type": "account_enum",
                    "confidence": "high", "entity_type": "username"
                } for h in hits]
            tasks.append(_safe_run(_run_maigret()))

        elif target_type == "domain":
            domain = variants["original"]
            async def _run_crtsh():
                import requests
                try:
                    # Crts.sh lookup
                    url = f"https://crt.sh/?q={domain}&output=json"
                    # Using thread executor for blocking sync call
                    def fetch():
                        return requests.get(url, timeout=10).json()
                    loop = asyncio.get_running_loop()
                    data = await loop.run_in_executor(None, fetch)

                    hits = []
                    seen_subs = set()
                    for entry in data:
                        name_value = entry.get("name_value", "")
                        for sub in name_value.split("\n"):
                            if sub and sub not in seen_subs and not sub.startswith("*"):
                                seen_subs.add(sub)
                                hits.append({
                                    "title": f"Subdomain: {sub}", "url": f"https://{sub}",
                                    "snippet": f"Certificate transparency log for {sub}",
                                    "source_tool": "crtsh", "source_type": "infra",
                                    "confidence": "high", "entity_type": "domain"
                                })
                    return hits
                except Exception as e:
                    logger.error(f"crt.sh failed: {e}")
                    return []

            async def _run_rdap():
                import requests
                try:
                    url = f"https://rdap.org/domain/{domain}"
                    def fetch_rdap():
                        return requests.get(url, timeout=10).json()
                    loop = asyncio.get_running_loop()
                    data = await loop.run_in_executor(None, fetch_rdap)

                    hits = []
                    if "handle" in data or "name" in data:
                        hits.append({
                            "title": f"RDAP Handle: {data.get('handle', domain)}",
                            "url": url,
                            "snippet": f"RDAP Registration info for {domain}. Entities: {len(data.get('entities', []))}",
                            "source_tool": "rdap", "source_type": "registry",
                            "confidence": "high", "entity_type": "domain"
                        })
                    return hits
                except Exception as e:
                    logger.error(f"RDAP failed: {e}")
                    return []

            tasks.append(_safe_run(_run_crtsh()))
            tasks.append(_safe_run(_run_rdap()))

        if tasks:
            completed = await asyncio.gather(*tasks, return_exceptions=True)
            for res_list in completed:
                if isinstance(res_list, list):
                    results.extend(res_list)

        return results

    async def _run_stage_2_serp(self, target_type: str, variants: Dict[str, Any], stage1_results: List[Dict[str, Any]], stop_event) -> List[Dict[str, Any]]:
        results = []

        # Only run SERP if no or few results were found in Stage 1, or to fill specific gaps.
        if len(stage1_results) > 5 and target_type not in ["person", "company"]:
            return results

        async def _safe_run(coro):
            async with self.semaphore:
                try:
                    return await coro
                except Exception as e:
                    logger.error(f"SERP source failed: {e}")
                    return []

        def _map_to_unified(hits, source_tool, entity_type):
            mapped = []
            if isinstance(hits, dict):
                for cat, items in hits.items():
                    for h in items:
                        mapped.append({
                            "title": h.get("title", ""), "url": h.get("url", ""), "snippet": h.get("snippet", ""),
                            "source_tool": source_tool, "source_type": "serp",
                            "confidence": "low", "entity_type": entity_type
                        })
            elif isinstance(hits, list):
                for h in hits:
                    mapped.append({
                        "title": h.get("title", ""), "url": h.get("url", ""), "snippet": h.get("snippet", ""),
                        "source_tool": source_tool, "source_type": "serp",
                        "confidence": "low", "entity_type": entity_type
                    })
            return mapped

        # Instead of calling synchronous functions directly, we wrap them in executor
        # Or ideally we should call the async equivalent if they existed. The existing codebase uses sync requests.Session in PhoneOSINT, CompanyOSINT etc.
        import concurrent.futures
        loop = asyncio.get_running_loop()

        if target_type == "phone":
            from sherlock_project.phone_search import PhoneOSINT
            po = PhoneOSINT()
            meta = variants.get("meta", {})
            if meta.get("valid"):
                def _run():
                    # We run advanced dorks
                    return po.search_phone_advanced_dorks(meta, stop_event)
                hits = await loop.run_in_executor(None, _run)
                results.extend(_map_to_unified(hits, "bing/ddg", "phone"))

        elif target_type == "company":
            from sherlock_project.company_search import CompanyOSINT
            co = CompanyOSINT()
            company_name = variants["original"]
            def _run():
                return co.search_company(company_name, country_filter="Alle", stop_event=stop_event)
            hits = await loop.run_in_executor(None, _run)
            results.extend(_map_to_unified(hits, "bing/ddg", "company"))

        elif target_type == "person":
            from sherlock_project.person_search import PersonOSINT
            po = PersonOSINT()
            first, last, extra = variants["original"]
            def _run():
                return po.search_person(first, last, extra, stop_event=stop_event)
            hits = await loop.run_in_executor(None, _run)
            results.extend(_map_to_unified(hits, "bing/ddg", "person"))

        elif target_type == "username":
            from sherlock_project.phone_search import PhoneOSINT
            po = PhoneOSINT()
            username = variants["original"]
            def _run():
                return po.search_username_advanced_dorks(username, stop_event)
            hits = await loop.run_in_executor(None, _run)
            results.extend(_map_to_unified(hits, "bing/ddg", "username"))

        return results

    async def _run_stage_3_pivots(self, target_type: str, results: List[Dict[str, Any]], stop_event) -> List[Dict[str, Any]]:
        pivoted_results = []

        # Example conditional pivots:
        # If target was company and we found a domain (url), pivot to crt.sh
        if target_type == "company":
            seen_domains = set()
            import urllib.parse
            for r in results:
                try:
                    parsed = urllib.parse.urlparse(r["url"])
                    domain = parsed.netloc.replace("www.", "")
                    if domain and domain not in seen_domains and "." in domain:
                        seen_domains.add(domain)
                        # Avoid pivoting on huge platforms
                        if not any(plat in domain for plat in ["linkedin.com", "facebook.com", "twitter.com", "instagram.com", "kvk.nl", "openkvk.nl", "companyinfo.nl", "drimble.nl"]):
                            # Pivot domain
                            variants = await self._run_stage_0_normalize("domain", domain)
                            sub_results = await self._run_stage_1_authoritative("domain", variants, stop_event)
                            pivoted_results.extend(sub_results)
                except Exception:
                    pass

        return pivoted_results

    async def _run_stage_4_fusion(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dedupe on normalized URL + title fingerprint, assign confidence, cross-link entities.
        """
        fused = []
        seen = set()

        for r in raw_results:
            url = r.get("url", "").lower().rstrip("/")
            title = r.get("title", "")
            fingerprint = f"{url}|{title}"

            if fingerprint not in seen:
                seen.add(fingerprint)
                fused.append(r)

        return fused

    def _run_stage_5_ranking(self, fused_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank: source authority > exact token match > SERP noise
        """
        def rank_score(res):
            conf = res.get("confidence", "low")
            if conf == "high": return 3
            if conf == "medium": return 2
            return 1

        return sorted(fused_results, key=rank_score, reverse=True)

    def post_message(self, msg: str):
        if self.ui_callback_msg:
            self.ui_callback_msg(msg + "\n")

    def post_progress(self, current: int, total: int):
        if self.ui_callback_progress and total > 0:
            self.ui_callback_progress(current, total)

    def post_result(self, result: Dict[str, Any]):
        if self.ui_callback_result:
            cat = result.get("source_type", "general")
            self.ui_callback_result(cat, result)
