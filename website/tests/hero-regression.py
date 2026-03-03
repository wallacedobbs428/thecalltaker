#!/usr/bin/env python3
"""
Hero headline regression test — prevents "Receptionist" from ever breaking again.

Two layers:
  Layer 1 (static): Parse index.html source — assert CSS rules, HTML structure,
                     and JS text scatter are correct. Zero dependencies, fast, CI-safe.
  Layer 2 (live):   Optional headless Chrome check at 5 viewports. Runs locally
                     or in CI with Chrome/Chromium installed.

Usage:
  python3 website/tests/hero-regression.py              # static only (CI default)
  python3 website/tests/hero-regression.py --live        # static + live Chrome check
  python3 website/tests/hero-regression.py --live --url http://localhost:8080

Exit codes: 0 = all pass, 1 = failure(s)
"""
import re, sys, os

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


# ─── LAYER 1: STATIC SOURCE ANALYSIS ─────────────────────────────────

def run_static():
    print("=== Layer 1: Static Source Analysis ===")
    print(f"File: {INDEX}\n")

    with open(INDEX, "r") as f:
        src = f.read()

    # 1. CSS: .hero h1 has display: block
    hero_h1_block = re.search(r'\.hero\s+h1\s*\{[^}]*display:\s*block', src)
    if hero_h1_block:
        ok(".hero h1 CSS has display: block")
    else:
        fail(".hero h1 CSS missing display: block")

    # 2. CSS: .hero h1 has word-break: normal
    hero_h1_wb = re.search(r'\.hero\s+h1\s*\{[^}]*word-break:\s*normal', src)
    if hero_h1_wb:
        ok(".hero h1 CSS has word-break: normal")
    else:
        fail(".hero h1 CSS missing word-break: normal")

    # 3. CSS: .hero h1 has overflow-wrap: normal
    hero_h1_ow = re.search(r'\.hero\s+h1\s*\{[^}]*overflow-wrap:\s*normal', src)
    if hero_h1_ow:
        ok(".hero h1 CSS has overflow-wrap: normal")
    else:
        fail(".hero h1 CSS missing overflow-wrap: normal")

    # 4. CSS: .hero h1 has hyphens: none
    hero_h1_hyp = re.search(r'\.hero\s+h1\s*\{[^}]*hyphens:\s*none', src)
    if hero_h1_hyp:
        ok(".hero h1 CSS has hyphens: none")
    else:
        fail(".hero h1 CSS missing hyphens: none")

    # 5. CSS: .no-break-word class exists with white-space: nowrap
    nbw_class = re.search(r'\.no-break-word\s*\{[^}]*white-space:\s*nowrap', src)
    if nbw_class:
        ok(".no-break-word class has white-space: nowrap")
    else:
        fail(".no-break-word class missing or lacks white-space: nowrap")

    # 6. HTML: h1 contains <span class="no-break-word">Receptionist</span>
    h1_span = re.search(
        r'<h1>[^<]*<span\s+class="no-break-word">Receptionist</span>[^<]*</h1>',
        src
    )
    if h1_span:
        ok('H1 contains <span class="no-break-word">Receptionist</span>')
    else:
        fail('H1 missing <span class="no-break-word">Receptionist</span>')

    # 7. HTML: h1 text reads "An AI Receptionist Trained For Your Business"
    h1_match = re.search(r'<h1>(.*?)</h1>', src, re.DOTALL)
    if h1_match:
        h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        if "Receptionist" in h1_text and "Trained" in h1_text:
            ok(f'H1 text intact: "{h1_text[:60]}..."')
        else:
            fail(f'H1 text changed: "{h1_text[:80]}"')
    else:
        fail("No <h1> found in hero section")

    # 8. JS: text scatter sets display: block (NOT inline)
    scatter_display = re.search(r"heroH1\.style\.display\s*=\s*'block'", src)
    if scatter_display:
        ok("Text scatter sets h1 display to 'block'")
    else:
        fail("Text scatter missing display='block' (may be 'inline' — DANGER)")

    # 9. JS: text scatter does NOT set display: inline
    scatter_inline = re.search(r"heroH1\.style\.display\s*=\s*'inline'", src)
    if not scatter_inline:
        ok("Text scatter does NOT set display: inline")
    else:
        fail("Text scatter sets display: inline — THIS WILL BREAK THE HEADLINE")

    # 10. JS: text scatter uses word-level grouping (nowrap word wrappers)
    scatter_words = re.search(r"white-space:\s*nowrap.*display:\s*inline-block", src)
    if scatter_words:
        ok("Text scatter uses nowrap word-level grouping")
    else:
        fail("Text scatter missing word-level nowrap grouping")

    # 11. JS: text scatter splits by words (not just characters)
    scatter_split = re.search(r"txt\.split\(\s*/\\s\+/\s*\)", src)
    if scatter_split:
        ok("Text scatter splits text by words")
    else:
        fail("Text scatter may not split by words (character-level = breaks words)")


# ─── LAYER 2: LIVE HEADLESS CHROME ────────────────────────────────────

def run_live(url):
    import subprocess, json, time

    print("\n=== Layer 2: Live Headless Chrome ===")
    print(f"URL: {url}\n")

    viewports = [320, 375, 414, 768, 1200]

    # Find Chrome
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome-stable",
        "google-chrome",
        "chromium-browser",
        "chromium",
    ]
    chrome_bin = None
    for p in chrome_paths:
        try:
            subprocess.run([p, "--version"], capture_output=True, timeout=5)
            chrome_bin = p
            break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if not chrome_bin:
        print("  SKIP  Chrome/Chromium not found — skipping live checks")
        return

    # Serve website locally if URL is localhost
    server_proc = None
    if "localhost" in url or "127.0.0.1" in url:
        import socket
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

    js_payload = r"""
    (function() {
      var h1 = document.querySelector('.hero h1');
      if (!h1) return 'NO_H1';
      var text = h1.innerText || h1.textContent;
      var style = window.getComputedStyle(h1);
      var nbw = h1.querySelector('.no-break-word');
      var nbwWS = nbw ? window.getComputedStyle(nbw).whiteSpace : 'N/A';
      var wordGroups = h1.querySelectorAll('span[style*="nowrap"]').length;
      return [
        'TEXT=' + text.replace(/\n/g, ' '),
        'DISPLAY=' + style.display,
        'WORD_BREAK=' + style.wordBreak,
        'HYPHENS=' + (style.hyphens || style.webkitHyphens || 'N/A'),
        'NBW_WS=' + nbwWS,
        'SCATTER_GROUPS=' + wordGroups
      ].join('|');
    })();
    """.strip()

    # Create wrapper page that navigates and reports via <title>
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

        text = fields.get("TEXT", "")
        display = fields.get("DISPLAY", "?")
        hyphens = fields.get("HYPHENS", "?")
        nbw_ws = fields.get("NBW_WS", "?")
        groups = int(fields.get("SCATTER_GROUPS", "0"))

        # Check 1: "Receptionist" in text
        if "Receptionist" in text:
            ok(f"[{w}px] H1 text contains 'Receptionist'")
        else:
            fail(f"[{w}px] H1 text missing 'Receptionist': {text[:60]}")

        # Check 2: display: block
        if display == "block":
            ok(f"[{w}px] h1 display: block")
        else:
            fail(f"[{w}px] h1 display: {display} (expected block)")

        # Check 3: .no-break-word nowrap OR scatter word groups
        if nbw_ws == "nowrap":
            ok(f"[{w}px] .no-break-word white-space: nowrap")
        elif groups >= 5:
            ok(f"[{w}px] Text scatter has {groups} word groups (nowrap)")
        else:
            fail(f"[{w}px] No nowrap protection (nbw={nbw_ws}, groups={groups})")

        # Check 4: hyphens
        if hyphens in ("none", "manual"):
            ok(f"[{w}px] h1 hyphens: {hyphens}")
        else:
            fail(f"[{w}px] h1 hyphens: {hyphens} (expected none)")

    if server_proc:
        server_proc.terminate()


# ─── MAIN ─────────────────────────────────────────────────────────────

def main():
    print("Hero Headline Regression Test")
    print("=" * 60)

    run_static()

    if "--live" in sys.argv:
        url = "https://thecalltaker.com"
        for i, arg in enumerate(sys.argv):
            if arg == "--url" and i + 1 < len(sys.argv):
                url = sys.argv[i + 1]
        run_live(url)

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
