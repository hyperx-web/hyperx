# Record the research-page animations to PNG frame sequences with headless Edge (Chrome DevTools Protocol).
#   SVG figures: loaded in an <object>, SMIL clock stepped with pauseAnimations()/setCurrentTime().
#   Canvas figures: research page with performance.now / requestAnimationFrame replaced by a manual clock.
# Needs the local preview served at http://localhost:8765 (see CLAUDE.md). Frames go to <out>/<name>/%04d.png;
# tools/frames_to_mp4.m turns them into H.264 MP4 with MATLAB.
# Usage: python tools/record_anims.py <out_dir> [name ...]
import base64, json, os, subprocess, sys, time, urllib.request
import websocket

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = "http://localhost:8765"
SITE = os.environ.get("PREVIEW_SITE", "")       # folder served at BASE (the preview _site)
FPS = 20
SVGS = {   # name: (file, seconds, css width)
    "ai-rlbf": ("ai-rlbf-anim.svg", 14.0, 1500),
    "ai-btnws": ("ai-btnws-anim.svg", 7.2, 1500),
    "ai-agent": ("ai-agent-anim.svg", 16.8, 1500),
    "6g-rsma": ("6g-rsma-anim.svg", 7.2, 1400),
    "6g-afdm": ("6g-afdm-anim.svg", 7.2, 1500),
}
CANVAS = {  # name: (canvas selector, seconds)
    "sat-constellation": ("canvas.constellation", 16.0),
    "sat-beams": ("canvas.efbeam", 8.0),
    "sat-threebody": ("canvas.threebody", 14.0),
}
CLOCK = """
(function(){ var T = 0, q = [];
  performance.now = function(){ return T; };
  window.requestAnimationFrame = function(cb){ q.push(cb); return q.length; };
  window.__step = function(dt){ T += dt; var c = q; q = []; c.forEach(function(f){ f(T); }); };
})();"""


class CDP:
    def __init__(self, port):
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
        page = [t for t in tabs if t["type"] == "page"][0]
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        self.n = 0

    def call(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        return r.get("result", {}).get("value")

    def shot(self, path, clip):
        r = self.call("Page.captureScreenshot", format="png", clip=dict(clip, scale=1), captureBeyondViewport=True)
        open(path, "wb").write(base64.b64decode(r["data"]))


def main():
    out = sys.argv[1]
    names = sys.argv[2:] or list(SVGS) + list(CANVAS)
    port = 9333
    prof = os.path.join(out, f"_edge_profile_{os.getpid()}")
    proc = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
                             "--hide-scrollbars", "--no-first-run", "--window-size=1600,1200", "about:blank"])
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/json"); break
            except Exception:
                time.sleep(0.5)
        c = CDP(port)
        c.call("Page.enable"); c.call("Runtime.enable")
        for name in names:
            d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
            if name in SVGS:
                f, secs, w = SVGS[name]
                c.call("Emulation.setDeviceMetricsOverride", width=1600, height=1200, deviceScaleFactor=1.25, mobile=False)
                vb = open(os.path.join("assets/img/research", f), encoding="utf-8").read(4000)
                import re as _re
                vw, vh = [float(v) for v in _re.search(r'viewBox="([^"]+)"', vb).group(1).split()[2:]]
                h = round(w * vh / vw)
                # same-origin page (written into the served preview root) so contentDocument is reachable
                page = (f"<html><body style='margin:0;background:#fff'><object id=o type='image/svg+xml' "
                        f"data='/assets/img/research/{f}' style='width:{w}px;height:{h}px;display:block'></object></body></html>")
                open(os.path.join(SITE, "_rec.html"), "w", encoding="utf-8").write(page)
                c.call("Page.navigate", url=f"{BASE}/_rec.html?{time.time()}")
                time.sleep(2.5)
                c.js("(function(){var s=document.getElementById('o').contentDocument.documentElement; s.pauseAnimations(); return 1})()")
                r = c.js("JSON.stringify(document.getElementById('o').getBoundingClientRect())")
                r = json.loads(r); clip = {"x": r["x"], "y": r["y"], "width": r["width"], "height": r["height"]}
                for k in range(int(secs * FPS)):
                    c.js(f"document.getElementById('o').contentDocument.documentElement.setCurrentTime({k / FPS})")
                    c.shot(os.path.join(d, f"{k:04d}.png"), clip)
            else:
                sel, secs = CANVAS[name]
                c.call("Emulation.setDeviceMetricsOverride", width=1280, height=900, deviceScaleFactor=2, mobile=False)   # canvas backing store = 3x CSS size
                sid = c.call("Page.addScriptToEvaluateOnNewDocument", source=CLOCK)["identifier"]
                c.call("Page.navigate", url=f"{BASE}/research/?rec={time.time()}")
                time.sleep(3)
                c.js("document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in')}); 1")
                for _ in range(5):
                    c.js("__step(16)")
                time.sleep(0.5)
                for k in range(int(secs * FPS)):            # read the canvas pixels directly (screenshots of off-screen canvases come out blank)
                    c.js(f"__step({1000 / FPS})")
                    url = c.js(f"document.querySelector('{sel}').toDataURL('image/png')")
                    open(os.path.join(d, f"{k:04d}.png"), "wb").write(base64.b64decode(url.split(",", 1)[1]))
                c.call("Page.removeScriptToEvaluateOnNewDocument", identifier=sid)
            print(name, "frames:", len(os.listdir(d)), flush=True)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
