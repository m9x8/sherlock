import re
import urllib.parse
from typing import List, Dict

def filter_and_rank_results(results: List[Dict[str, str]], query: str, top_k: int = 8) -> List[Dict[str, str]]:
    if not results:
        return []

    # 1. Extract tokens from query
    clean_query = re.sub(r'(site|intitle|inurl|intext|filetype|ext):\S+', '', query)
    clean_query = re.sub(r'[^\w\s]', ' ', clean_query)
    stopwords = {"the", "and", "for", "with", "van", "der", "de", "het", "een", "en", "op", "te", "in", "or", "to", "is", "of", "aan"}
    tokens = set(word.lower() for word in clean_query.split() if len(word) >= 3 and word.lower() not in stopwords)

    # 2. Noise patterns
    noise_patterns = [
        r'/schemas/', r'/dataservice/', r'/status', r'/incident',
        r'api-docs', r'swagger', r'/login', r'/auth',
        r'index of /', r'directory listing', r'vulnerability',
        r'\.json$', r'\.xml$'
    ]
    noise_regex = re.compile('|'.join(noise_patterns), re.IGNORECASE)

    filtered_results = []
    seen_urls = set()

    for hit in results:
        url = hit.get("url", "")
        title = hit.get("title", "")
        snippet = hit.get("snippet", "")

        # Decode URL
        try:
            decoded_url = urllib.parse.unquote(url)
        except Exception:
            decoded_url = url

        hit["url"] = decoded_url

        # Normalize URL for deduplication
        norm_url = decoded_url.rstrip('/').lower()
        if norm_url in seen_urls:
            continue

        # Check noise
        if noise_regex.search(decoded_url) or noise_regex.search(title):
            continue

        # Score overlap
        combined_text = f"{title} {snippet} {decoded_url}".lower()
        score = sum(1 for token in tokens if token in combined_text)

        # Require some relevance if tokens exist
        if tokens and score == 0:
            continue

        # Clean snippet
        clean_snippet = re.sub(r'%[0-9A-Fa-f]{2}', '', snippet)
        clean_snippet = re.sub(r'\s+', ' ', clean_snippet).strip()
        hit["snippet"] = clean_snippet
        hit["score"] = score

        seen_urls.add(norm_url)
        filtered_results.append(hit)

    filtered_results.sort(key=lambda x: x["score"], reverse=True)

    for hit in filtered_results:
        hit.pop("score", None)

    return filtered_results[:top_k]
