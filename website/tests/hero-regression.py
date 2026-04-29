#!/usr/bin/env python3
"""
Hero headline regression test — prevents word-breaking regressions.

Two layers:
  Layer 1 (static): Parse index.html source — assert CSS rules, HTML structure.
                     Zero dependencies, fast, CI-safe.
  Layer 2 (live):   Optional headless Chrome check at 5 viewports. Runs locally
                     or in CI with Chrome/Chromium installed.

Usage:
  python3 website/tests/hero-regression.py              # static only (CI default)
  python3 website/tests/hero-regression.py --live        # static + live Chrome check
  python3 website/tests/hero-regression.py --live --url http://localhost:8080
  python3 website/tests/hero-regression.py --live --screenshots ./artifacts

Exit codes: 0 = all pass, 1 = failure(s)
"""
import re, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX = os.path.join(ROOT, "website", "index.html")

passes = 0
failures = []


def ok(label):
    global passes
    passes += 1
    print(f"  PASS  {label}")


def fail(label):
    failures.append(label)
    print(f"  FAIL  {label}")


# --- LAYER 1: STATIC SOURCE ANALYSIS ---

def run_static():
    print("=== Layer 1: Static Source Analysis ===")
    print(f"File: {INDEX}\n")

    with open(INDEX, "r") as f:
        src = f.read()

    # 1. CSS: .hero h1 has display: block
    if re.search(r'\.hero\s+h1\s*\{[^}]*display:\s*block', src):
        ok(".hero h1 CSS has display: block")
    else:
        fail(".hero h1 CSS missing display: block")

    # 2. CSS: .hero h1 has word-break: normal
    if re.search(r'\.hero\s+h1\s*\{[^}]*word-break:\s*normal', src):
        ok(".hero h1 CSS has word-break: normal")
    else:
        fail(".hero h1 CSS missing word-break: normal")

    # 3. CSS: .hero h1 has overflow-wrap: normal
    if re.search(r'\.hero\s+h1\s*\{[^}]*overflow-wrap:\s*normal', src):
        ok(".hero h1 CSS has overflow-wrap: normal")
    else:
        fail(".hero h1 CSS missing overflow-wrap: normal")

    # 4. CSS: .hero h1 has hyphens: none
    if re.search(r'\.hero\s+h1\s*\{[^}]*hyphens:\s*none', src):
        ok(".hero h1 CSS has hyphens: none")
    else:
        fail(".hero h1 CSS missing hyphens: none")

    # 5. CSS: .no-break-word class exists with white-space: nowrap
    if re.search(r'\.no-break-word\s*\{[^}]*white-space:\s*nowrap', src):
        ok(".no-break-word class has white-space: nowrap")
    else:
        fail(".no-break-word class missing or lacks white-space: nowrap")

    # 6. HTML: h1 contains <span class="no-break-word"> wrapping multi-word phrase
    h1_markup = re.search(r'<h1\b[^>]*>(.*?)</h1>', src, re.DOTALL)
    if h1_markup and re.search(
        r'<span\s+class="no-break-word">[^<]+</span>',
        h1_markup.group(1),
    ):
        ok('H1 contains <span class="no-break-word"> protecting a phrase')
    else:
        fail('H1 missing <span class="no-break-word"> protection')

    # 7. HTML: h1 text is current copy
    h1_match = re.search(r'<h1>(.*?)</h1>', src, re.DOTALL)
    if h1_match:
        h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        if "It's 2 AM" in h1_text and "Gideon answers" in h1_text:
            ok(f'H1 text intact: "{h1_text[:60]}"')
        else:
            fail(f'H1 text changed: "{h1_text[:80]}"')
    else:
        fail("No <h1> found in hero section")

    # 8. CSS: .hero h1 does NOT have display: inline
    if not re.search(r'\.hero\s+h1\s*\{[^}]*display:\s*inline[^-]', src):
        ok(".hero h1 does NOT set display: inline")
    else:
        fail(".hero h1 has display: inline — THIS WILL BREAK THE HEADLINE")


# --- LAYER 2: LIVE HEADLESS CHROME ---

def find_chrome():
    """Find Chrome/Chromium binary."""
    for p in [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome-stable",
        "google-chrome",
        "chromium-browser",
        "chromium",
    ]:
        try:
            subprocess.run([p, "--version"], capture_output=True, timeout=5)
            return p
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def capture_screenshots(chrome_bin, url, out_dir):
    """Capture hero screenshots at 320px and 1200px."""
    os.makedirs(out_dir, exist_ok=True)
    for w in [320, 1200]:
        out_path = os.path.join(out_dir, f"hero-{w}.png")
        subprocess.run(
            [chrome_bin, "--headless=new", "--disable-gpu", "--no-sandbox",
             f"--window-size={w},900",
             f"--screenshot={out_path}",
             url],
            capture_output=True, timeout=30,
        )
        if os.path.exists(out_path):
            size_kb = os.path.getsize(out_path) / 1024
            print(f"  SAVED {out_path} ({size_kb:.0f} KB)")
        else:
            print(f"  WARN  Failed to capture {w}px screenshot")


def run_live(url, screenshot_dir=None):
    import json, time

    print("\n=== Layer 2: Live Headless Chrome ===")
    print(f"URL: {url}\n")

    viewports = [320, 375, 414, 768, 1200]

    chrome_bin = find_chrome()
    if not chrome_bin:
        print("  SKIP  Chrome/Chromium not found — skipping live checks")
        return

    server_proc = None
    if "localhost" in url or "127.0.0.1" in url:
        port = int(url.split(":")[-1].rstrip("/")) if ":" in url.split("//")[-1] else 8765
        website_dir = os.path.join(ROOT, "website")
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port)],
            cwd=website_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
        url = f"http://localhost:{port}"

    if screenshot_dir:
        print("--- Screenshots ---")
        capture_screenshots(chrome_bin, url + "/index.html", screenshot_dir)
        print()

    js_payload = r"""
    (function() {
      var h1 = document.querySelector('.hero h1');
      if (!h1) return 'NO_H1';
      var text = h1.innerText || h1.textContent;
      var style = window.getComputedStyle(h1);
      var nbw = h1.querySelector('.no-break-word');
      var nbwWS = nbw ? window.getComputedStyle(nbw).whiteSpace : 'N/A';
      return [
        'TEXT=' + text.replace(/\n/g, ' '),
        'DISPLAY=' + style.display,
        'WORD_BREAK=' + style.wordBreak,
        'HYPHENS=' + (style.hyphens || style.webkitHyphens || 'N/A'),
        'NBW_WS=' + nbwWS
      ].join('|');
    })();
    """.strip()

    for w in viewports:
        wrapper = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script>
fetch('{url}/index.html').then(function(r){{return r.text()}}).then(function(html){{
  document.open(); document.write(html); document.close();
  setTimeout(function(){{ document.title='R:'+eval({json.dumps(js_payload)}); }}, 3000);
}}).catch(function(e){{ document.title='R:ERROR='+e.message; }});
</script></head><body></body></html>"""

        wrapper_path = f"/tmp/hero-test-{w}.html"
        with open(wrapper_path, "w") as f:
            f.write(wrapper)

        result = subprocess.run(
            [chrome_bin, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--disable-web-security", "--allow-file-access-from-files",
             f"--window-size={w},900",
             "--virtual-time-budget=10000",
             "--dump-dom", f"file://{wrapper_path}"],
            capture_output=True, text=True, timeout=30
        )

        title_match = re.search(r'<title>R:(.*?)</title>', result.stdout)
        if not title_match:
            print(f"  [{w}px] SKIP  Could not extract results")
            continue

        data = title_match.group(1)
        if data.startswith("ERROR"):
            print(f"  [{w}px] SKIP  {data}")
            continue

        fields = dict(kv.split("=", 1) for kv in data.split("|") if "=" in kv)

        display = fields.get("DISPLAY", "?")
        hyphens = fields.get("HYPHENS", "?")
        nbw_ws = fields.get("NBW_WS", "?")

        if display == "block":
            ok(f"[{w}px] h1 display: block")
        else:
            fail(f"[{w}px] h1 display: {display} (expected block)")

        if nbw_ws == "nowrap":
            ok(f"[{w}px] .no-break-word white-space: nowrap")
        else:
            fail(f"[{w}px] No nowrap protection (nbw={nbw_ws})")

        if hyphens in ("none", "manual"):
            ok(f"[{w}px] h1 hyphens: {hyphens}")
        else:
            fail(f"[{w}px] h1 hyphens: {hyphens} (expected none)")

    if server_proc:
        server_proc.terminate()


# --- MAIN ---

def main():
    print("Hero Headline Regression Test")
    print("=" * 60)

    run_static()

    if "--live" in sys.argv:
        url = "https://thecalltaker.com"
        screenshot_dir = None
        for i, arg in enumerate(sys.argv):
            if arg == "--url" and i + 1 < len(sys.argv):
                url = sys.argv[i + 1]
            if arg == "--screenshots" and i + 1 < len(sys.argv):
                screenshot_dir = sys.argv[i + 1]
        run_live(url, screenshot_dir=screenshot_dir)

    print("\n" + "=" * 60)
    print(f"Results: {passes} passed, {len(failures)} failed")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nAll checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
