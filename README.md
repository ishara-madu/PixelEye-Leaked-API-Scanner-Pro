# 🛸 PixelEye Leaked API Scanner Pro

PixelEye Leaked API Scanner Pro is a high-performance, stealthy, and modular security tool designed to discover, extract, and validate leaked API keys across various platforms. Featuring a premium dark-mode GUI and a multi-threaded validation engine, it provides a seamless workflow from discovery to live testing.

![Scanner Dashboard](scanner_dashboard_bg_1775738036331)

## 🌟 Key Features

*   **Multi-Platform Support**: Built-in presets for Gemini, ChatGPT, Claude, Groq, Mistral, Perplexity, DeepSeek, Google Maps, and OpenWeatherMap.
*   **Deep Scan Engine**: Advanced logic for Claude and ChatGPT that detects truncated GitHub snippets and automatically recovers full keys from raw source files.
*   **PixelEye Pro GUI**: A premium "OLED-dark" interface with real-time console logging and live status indicators.
*   **Multi-Format Export**: One-click downloads for discovered keys in **Excel (CSV)**, **JSON Array**, or **Standard Text** formats.
*   **Embedded API Tester**: Integrated visual environment for testing Google Maps and OpenWeatherMap keys directly from the dashboard.
*   **Custom Preset Manager**: Add, edit, or delete service configurations (keywords, regex patterns, validation endpoints) via the interactive settings module.
*   **Stealth Mode**: Automated scan delays, User-Agent rotation, and optional headless browsing to minimize rate-limiting triggers.

## 🚀 Getting Started

### Prerequisites

*   Python 3.10 or higher
*   Playwright (for browser automation)
*   Requests (for API validation)

### Installation

1.  **Clone the environment** (or ensure the files are in your directory):
    ```bash
    # Ensure you have the required Python libraries
    pip install playwright requests
    playwright install chromium
    ```

2.  **Run the Scanner**:
    ```bash
    python3 gui_scanner.py
    ```

## 🛠️ Usage Guide

1.  **Target Service**: Select a model from the dropdown (e.g., Claude or Gemini).
2.  **Depth**: Set the number of GitHub search pages to analyze (Deep Scans are handled automatically).
3.  **Initiate Scan**: Click the green button to begin.
4.  **Cancellation**: Safely abort a scan at any time using the red **CANCEL SCAN** toggle.
5.  **Verify & Export**: Use the **📥 DOWNLOAD** menu to save your valid keys to your system's Downloads folder.
6.  **Test Live**: Click **🛠️ OPEN API TESTER** to launch a visual testing environment for Maps and Weather keys.

## 💾 Storage & Persistence

*   **`presets.json`**: All your custom presets and model configurations are saved here.
*   **`{service}_keys.txt`**: Valid keys for each service are logged locally with discovery dates and status notes.

## ⚠️ Disclaimer

This tool is for educational and authorized security testing purposes only. Usage for unauthorized access or scanning of public repositories without appropriate permission is strictly prohibited. The authors are not responsible for any misuse of this software.

---
*Built with ❤️ by the PixelEye Team*
