# Sherlock Project (High-End Edition)

![Sherlock Banner](https://www.kali.org/tools/sherlock/images/sherlock-logo.svg)

**A professional, Zero-API, High-End OSINT (Open Source Intelligence) framework.**

This project is a deeply modified, advanced version of Sherlock. It features a complete **Graphical User Interface (GUI)**, **Phone Number OSINT**, **Company Reconnaissance**, **Dox Profiling**, and a sophisticated **Stealth Engine**.

## 🌟 Core Features

- **Zero-API & Zero-Proxy Architecture**: Features are 100% standalone. No paid APIs, no external proxy pools, and no mandatory registrations are required. All intelligence gathering uses advanced scraping and dorking techniques.
- **High-End Stealth Engine**: Utilizes asynchronous `curl_cffi` to rotate JA3/JA4 TLS fingerprints and impersonates real browser user-agents. It features DNS-over-HTTPS (DoH) rotation to bypass ISP logging and advanced anti-bot protections.
- **CustomTkinter GUI**: A beautiful, thread-safe, non-blocking desktop graphical user interface that streams realtime events and results without freezing.
- **Advanced OSINT Modules**:
  - **Phone OSINT**: Validates formats, retrieves carrier/geocoding data, and scrapes spam registries/dorks for real-time mentions.
  - **Company Recon**: Directly queries open business indexes (like OpenKVK) for live company intelligence.
  - **Dox & Person Profiling**: High-end dorking across leak sites, social media, and professional networks.
- **Comprehensive Reporting**: Export your findings seamlessly into TXT, Microsoft Word (.docx), or professionally styled PDF reports.

## 🚀 Usage

### Graphical Interface (GUI)

Launch the professional GUI built with CustomTkinter:

```bash
poetry run python -m sherlock_project.gui
```

*(Note: In headless environments, use `xvfb-run -a poetry run python -m sherlock_project.gui`)*

### Command Line Interface

```bash
poetry run sherlock --help
```

To search for a user across networks:
```bash
poetry run sherlock username123
```

## 🛠 Requirements

- Python >= 3.11, < 3.13
- Poetry (for dependency management)

## ⚖️ License

MIT License. See `LICENSE` for more information.
