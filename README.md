<p align=center>
  <br>
  <h1>🕵️ No Shit Sherlock</h1>
  <strong>The Ultimate Zero-API OSINT Framework</strong>
  <br><br>
</p>

## Overview

**No Shit Sherlock** is a high-end, extremely powerful Open Source Intelligence (OSINT) framework designed for professionals. It completely operates on a **Zero-API, Zero-Proxy** architecture, meaning it requires no paid API keys or mandatory proxy pools to deliver comprehensive investigative results.

By unifying cutting-edge networking techniques, asynchronous engines, and an extensive global site database, *No Shit Sherlock* allows you to perform deep reconnaissance entirely locally.

## Core Capabilities

1. **Deep Username Search (Maigret Integration)**
   - Leverages a massive 3000+ site database to scour the web for usernames.
   - Extracts comprehensive profile data, IDs, and metadata automatically without APIs.
   - Fully asynchronous and stealthy.

2. **Basic Username & Phone OSINT**
   - Search phone numbers and validate formats.
   - Carrier and geocoding metadata retrieval.
   - Scrape search engines and social platforms for public phone number mentions.

3. **Corporate & Person OSINT**
   - Hunt for public records, document leaks, and company affiliations entirely through advanced web crawling and zero-API engines.

4. **Stealth Networking Engine**
   - Utilizes `curl_cffi` for deep TLS and HTTP/2 fingerprint impersonation (JA3/JA4, Akamai spoofing).
   - Defeats rate limiters, basic WAFs (like Cloudflare), and IP bans effortlessly.

5. **Professional GUI**
   - Powered by CustomTkinter for a sleek, responsive, and dark-themed interface.
   - Thread-safe queues stream live results instantly without UI freezes.

## Installation & Usage

**Prerequisites:** Python 3.11 or 3.12, and `poetry` installed.

```bash
# Clone the repository
git clone https://github.com/your-repo/no-shit-sherlock.git
cd no-shit-sherlock

# Install dependencies with Poetry
poetry install

# Run the High-End GUI
poetry run sherlock --gui

# Or run headless in terminal
poetry run sherlock [username]
```

## Privacy & Ethics

**No Shit Sherlock** is designed for authorized, legal investigations, red-teaming, and cybersecurity research only. Do not use this framework for malicious activities, doxing, or stalking.
