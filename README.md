# No shit Sherlock - High-End OSINT Engine

Welcome to **No shit Sherlock**. This represents a fully standalone, zero-API, high-end reconnaissance framework designed for modern Open Source Intelligence (OSINT) gathering. By leveraging an advanced asynchronous core alongside the *Camoufox* cloaking framework, No shit Sherlock easily navigates and extracts data from even the most bot-resistant sources.

**DISCLAIMER & ETHICAL USAGE**
**This project is only intended to be used for ethical purposes. It should solely be utilized to search for your own digital footprint, or with explicit, documented permission from the target. Any misuse, malicious gathering of intelligence, or violations of privacy laws are strictly prohibited and the responsibility of the user.**

## Features (High-End 2026 Standards)

* **Zero-API Architecture**: No required subscriptions or paid external proxy pools. Everything runs natively and autonomously.
* **Undetectable Scraping**: Fully integrated with the `Camoufox` and `nodriver` bypass frameworks to evade advanced bot protections (CAPTCHAs, Cloudflare, TLS Fingerprinting, JA3/JA4 spoofing).
* **Multi-Vector Analysis**: Seamlessly perform in-depth searches across domains, phones, companies, people, and potential dox/leak footprints.
* **Asynchronous Networking Engine**: Utilizes `asyncio` and `curl_cffi` for lightning-fast, concurrent requests that maximize bandwidth while minimizing detection vectors.
* **Modern GUI**: Built on top of `CustomTkinter` offering a sleek, responsive, and intuitive cross-platform desktop application.
* **Real-time Visualization**: Bridges non-blocking intelligence engines directly into the synchronous GUI via thread-safe queuing.

## Requirements

Ensure you are running a modern Python environment:
- **Python >= 3.11, < 3.13**
- Poetry for dependency management

## Installation & Setup

### Windows Automated Setup (Recommended)
You can automatically install all dependencies, fetch browser binaries, and start the GUI using the provided `.bat` file:
```cmd
setup_and_run_windows.bat
```

### Manual Setup via Poetry

1. **Clone the repository:**
   ```bash
   git clone https://github.com/m9x8/no-shit-sherlok.git
   cd no-shit-sherlok
   ```

2. **Install Dependencies via Poetry:**
   ```bash
   poetry install
   ```

3. **Fetch Camoufox Engine (Required):**
   ```bash
   poetry run python -m camoufox fetch
   ```

4. **Run the Application:**
   ```bash
   poetry run python -m sherlock_project --gui
   ```
   *Note: In headless environments, you may need to emulate a display (e.g., using `xvfb-run -a env PYTHONPATH=. poetry run python -m sherlock_project --gui`).*

## Architecture Highlights

- **Stealth Engine:** Centralized connection manager that rotates browser profiles, modifies TLS extensions, and tweaks HTTP/2 parameters to randomize JA3, JA4, and Akamai fingerprints.
- **Scraper Engine:** High-performance direct scrapers leveraging Camoufox via a unified `StealthBrowser` abstraction for retrieving realtime OSINT data such as regional phone spam registries and company details without being blocked.
- **Reporting:** Exports detailed analytical findings into clean PDFs or DOCX formats for professional distribution.

## Contributing

We welcome professional-grade contributions that enhance the capabilities, stealth, or performance of the engine while maintaining its zero-API philosophy. Ensure all tests pass prior to submitting a pull request.

```bash
# Running tests
PYTHONPATH=. poetry run pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
