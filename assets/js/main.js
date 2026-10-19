(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Header background on scroll
  var header = document.querySelector(".site-header");
  function onScroll() { header.classList.toggle("scrolled", window.scrollY > 20); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  toggle.addEventListener("click", function () {
    var open = document.body.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", open);
  });

  // Reveal on scroll
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // Count-up stats
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var target = +el.dataset.count;
    if (reduceMotion || !target) return;
    el.textContent = "0";
    var started = false;
    var obs = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting || started) return;
      started = true;
      var t0 = performance.now();
      (function step(t) {
        var p = Math.min((t - t0) / 1400, 1);
        el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
    obs.observe(el);
  });

  // Starfield canvas
  document.querySelectorAll(".starfield").forEach(function (canvas) {
    var ctx = canvas.getContext("2d");
    var stars = [], w, h, dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round((w * h) / 5000);
      stars = [];
      for (var i = 0; i < n; i++) {
        stars.push({ x: Math.random() * w, y: Math.random() * h, r: Math.random() * 1.2 + 0.2,
          a: Math.random(), s: Math.random() * 0.02 + 0.004, v: Math.random() * 0.15 + 0.02 });
      }
    }
    function draw() {
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        s.a += s.s; s.x -= s.v;
        if (s.x < 0) s.x = w;
        ctx.globalAlpha = 0.35 + Math.abs(Math.sin(s.a)) * 0.65;
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2); ctx.fill();
      }
      if (!reduceMotion) requestAnimationFrame(draw);
    }
    resize(); draw();
    window.addEventListener("resize", resize);
  });

  // News: collapse after N items
  var list = document.querySelector("[data-collapsible]");
  if (list) {
    var limit = +list.dataset.collapsible;
    var items = list.querySelectorAll(".news-item");
    var btn = document.querySelector(".show-more");
    if (items.length > limit) {
      items.forEach(function (li, i) { if (i >= limit) li.classList.add("collapsed"); });
      btn.hidden = false;
      btn.addEventListener("click", function () {
        items.forEach(function (li) { li.classList.remove("collapsed"); li.classList.add("in"); });
        btn.hidden = true;
      });
    }
  }

  // Publications: filter + search
  var filters = document.querySelectorAll(".filter");
  var search = document.querySelector(".pub-search");
  if (filters.length) {
    var current = "all";
    var groups = document.querySelectorAll(".pub-group");
    var empty = document.querySelector(".no-results");
    function apply() {
      var q = (search.value || "").trim().toLowerCase();
      var any = false;
      groups.forEach(function (g) {
        var catOk = current === "all" || g.dataset.category === current;
        var visible = 0;
        g.querySelectorAll(".pub-item").forEach(function (it) {
          var ok = catOk && (!q || it.textContent.toLowerCase().indexOf(q) !== -1);
          it.classList.toggle("hidden", !ok);
          if (ok) visible++;
        });
        g.classList.toggle("hidden", visible === 0);
        if (visible) any = true;
      });
      empty.hidden = any;
    }
    filters.forEach(function (f) {
      f.addEventListener("click", function () {
        filters.forEach(function (x) { x.classList.remove("active"); });
        f.classList.add("active");
        current = f.dataset.filter;
        apply();
      });
    });
    search.addEventListener("input", apply);
  }

  // Gallery lightbox (albums: data-srcs = "url|url|...", arrows / keys to browse)
  var lb = document.querySelector(".lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img"), lbCap = lb.querySelector("p");
    var prev = lb.querySelector(".prev"), next = lb.querySelector(".next");
    var list = [], idx = 0, cap = "";
    function showAt(i) {
      idx = (i + list.length) % list.length;
      lbImg.src = list[idx]; lbImg.alt = cap;
      lbCap.textContent = list.length > 1 ? cap + "  ·  " + (idx + 1) + " / " + list.length : cap;
      prev.hidden = next.hidden = list.length < 2;
    }
    document.querySelectorAll(".gallery-open").forEach(function (b) {
      b.addEventListener("click", function () {
        list = b.dataset.srcs.split("|"); cap = b.dataset.caption; showAt(0); lb.hidden = false;
      });
    });
    function close() { lb.hidden = true; }
    prev.addEventListener("click", function (e) { e.stopPropagation(); showAt(idx - 1); });
    next.addEventListener("click", function (e) { e.stopPropagation(); showAt(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target !== lbImg) close(); });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft") showAt(idx - 1);
      else if (e.key === "ArrowRight") showAt(idx + 1);
    });
  }
})();

// LEO mega-constellation (Walker-delta) animation
(function () {
  var canvases = document.querySelectorAll(".constellation");
  if (!canvases.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var D2R = Math.PI / 180;

  canvases.forEach(function (cv) {
    var ctx = cv.getContext("2d");
    var P = 24, S = 22, F = 1;             // planes, sats per plane, phasing
    var inc = 53 * D2R, ratio = 1.28;        // orbit radius / Earth radius (altitude exaggerated for visibility)
    var tilt = 23 * D2R;                     // viewing tilt
    var w, h, R, cx, cy, dpr = Math.min(Math.max((window.devicePixelRatio || 1) * 1.5, 2), 3);
    var t0 = performance.now();

    function size() {
      w = cv.clientWidth; h = cv.clientHeight;
      cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      R = Math.min(w * 0.34, h * 0.38); cx = w / 2; cy = h / 2;
    }
    // rotate around y (spin) then x (tilt), orthographic projection
    function proj(x, y, z, spin) {
      var c = Math.cos(spin), s = Math.sin(spin);
      var x1 = c * x + s * z, z1 = -s * x + c * z;
      var ct = Math.cos(tilt), st = Math.sin(tilt);
      var y2 = ct * y - st * z1, z2 = st * y + ct * z1;
      return [cx + x1 * R, cy - y2 * R, z2];
    }
    function satPos(p, k, t) {
      var raan = (360 / P) * p * D2R;
      var u = ((360 / S) * k + (360 * F / (P * S)) * p) * D2R + t;
      // position in orbital plane, then inclination, then RAAN (z = north)
      var xo = Math.cos(u), yo = Math.sin(u);
      var x = xo, y = yo * Math.cos(inc), z = yo * Math.sin(inc);
      var X = x * Math.cos(raan) - y * Math.sin(raan), Y = x * Math.sin(raan) + y * Math.cos(raan);
      // map: world north -> screen up (y)
      return [X * ratio, z * ratio, Y * ratio];
    }

    function frame(now) {
      var t = reduce ? 0 : (now - t0) / 1000;
      var spin = t * 0.08, orbitT = t * 0.35;
      ctx.clearRect(0, 0, w, h);

      // satellites positions (world + projected)
      var pts = [], raw = [];
      for (var p = 0; p < P; p++) {
        pts[p] = []; raw[p] = [];
        for (var k = 0; k < S; k++) { var q = satPos(p, k, orbitT); raw[p][k] = q; pts[p][k] = proj(q[0], q[1], q[2], spin); }
      }

      // back-side sats & links (behind earth)
      drawLayer(pts, false);

      // earth
      var g = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R);
      g.addColorStop(0, "#cfe0f7"); g.addColorStop(0.7, "#a9c6ec"); g.addColorStop(1, "#7fa5d8");
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
      // graticule
      ctx.strokeStyle = "rgba(40,70,120,.22)"; ctx.lineWidth = 0.7;
      for (var lat = -75; lat <= 75; lat += 15) drawCircle(function (a) {
        return [Math.cos(lat * D2R) * Math.cos(a), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.sin(a)];
      }, spin);
      for (var lon = 0; lon < 180; lon += 15) drawCircle(function (a) {
        return [Math.cos(a) * Math.cos(lon * D2R), Math.sin(a), Math.cos(a) * Math.sin(lon * D2R)];
      }, spin);

      // front-side sats & links
      drawLayer(pts, true);
      if (!drawTerminal(raw, pts, spin) && !reduce) t0 = now;   // UE went behind the Earth -> restart
      if (!reduce) requestAnimationFrame(frame);
    }

    // ground terminal near the equator (kept facing the viewer), serving + neighbouring satellites
    var UT_LAT = 5 * D2R, UT_VIEW = -62 * D2R, NEIGH = 4;   // 1 serving + 2nd–5th nearest
    // Earth-fixed UE: starts near the left limb and rotates with the Earth
    var UT = [Math.cos(UT_LAT) * Math.sin(UT_VIEW), Math.sin(UT_LAT), Math.cos(UT_LAT) * Math.cos(UT_VIEW)];
    function drawTerminal(raw, pts, spin) {
      var ut = UT;
      var vis = [];
      for (var p = 0; p < P; p++) for (var k = 0; k < S; k++) {
        var q = raw[p][k], d = [q[0] - ut[0], q[1] - ut[1], q[2] - ut[2]];
        if (d[0] * ut[0] + d[1] * ut[1] + d[2] * ut[2] <= 0) continue;          // below the horizon
        vis.push({ p: p, k: k, dist: Math.hypot(d[0], d[1], d[2]) });
      }
      vis.sort(function (a, b) { return a.dist - b.dist; });
      // legend (bottom-left), scales with the canvas
      var f = Math.max(11, w / 38), lx = f, ly = h - 2.6 * f;
      ctx.font = "500 " + f + "px Inter, sans-serif"; ctx.textBaseline = "middle";
      ctx.fillStyle = "#e03131"; ctx.beginPath(); ctx.arc(lx + f * .35, ly, f * .36, 0, 7); ctx.fill();
      ctx.fillStyle = "#333"; ctx.fillText("Connected", lx + f * 1.2, ly);
      ctx.fillStyle = "#ffd43b"; ctx.beginPath(); ctx.arc(lx + f * .35, ly + f * 1.5, f * .32, 0, 7); ctx.fill();
      ctx.strokeStyle = "#a07800"; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = "#333"; ctx.fillText("Candidates", lx + f * 1.2, ly + f * 1.5);
      ctx.textBaseline = "alphabetic";
      var u = proj(ut[0], ut[1], ut[2], spin);
      if (u[2] < 0) return false;                 // UE is on the far side of the Earth
      ctx.lineCap = "round";
      // neighbouring satellites: faint grey links
      for (var i = 1; i <= NEIGH && i < vis.length; i++) {
        var s = pts[vis[i].p][vis[i].k];
        ctx.strokeStyle = "rgba(60,60,60,.32)"; ctx.lineWidth = 1; ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.moveTo(u[0], u[1]); ctx.lineTo(s[0], s[1]); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = "#ffd43b"; ctx.beginPath(); ctx.arc(s[0], s[1], 3.4, 0, 7); ctx.fill();   // candidate satellites: yellow
        ctx.strokeStyle = "#a07800"; ctx.lineWidth = 1; ctx.stroke();
      }
      // serving satellite: red
      if (vis.length) {
        var sv = pts[vis[0].p][vis[0].k];
        ctx.strokeStyle = "#e03131"; ctx.lineWidth = 1.8;
        ctx.beginPath(); ctx.moveTo(u[0], u[1]); ctx.lineTo(sv[0], sv[1]); ctx.stroke();
        ctx.fillStyle = "#e03131"; ctx.beginPath(); ctx.arc(sv[0], sv[1], 4, 0, 7); ctx.fill();
        ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.2; ctx.stroke();
      }
      // terminal
      ctx.fillStyle = "#1b2f52";
      ctx.beginPath(); ctx.moveTo(u[0], u[1] - 6); ctx.lineTo(u[0] - 5, u[1] + 3); ctx.lineTo(u[0] + 5, u[1] + 3); ctx.closePath(); ctx.fill();
      ctx.font = "600 11px Inter, sans-serif"; ctx.fillText("UE", u[0] + 7, u[1] + 4);
      return true;
    }

    function drawCircle(fn, spin) {
      ctx.beginPath(); var started = false;
      for (var i = 0; i <= 72; i++) {
        var v = fn(i / 72 * Math.PI * 2), q = proj(v[0], v[1], v[2], spin);
        if (q[2] < 0) { started = false; continue; }
        if (!started) { ctx.moveTo(q[0], q[1]); started = true; } else ctx.lineTo(q[0], q[1]);
      }
      ctx.stroke();
    }
    function hidden(q) { // behind earth disk?
      if (q[2] >= 0) return false;
      var dx = q[0] - cx, dy = q[1] - cy;
      return dx * dx + dy * dy < R * R;
    }
    function drawLayer(pts, front) {
      for (var p2 = 0; p2 < P; p2++) for (var k2 = 0; k2 < S; k2++) {
        var s = pts[p2][k2];
        if ((s[2] >= 0) !== front) continue;
        if (!front && hidden(s)) continue;
        ctx.fillStyle = front ? "#1b2f52" : "rgba(27,47,82,.25)";
        ctx.beginPath(); ctx.arc(s[0], s[1], front ? 1.8 : 1.2, 0, Math.PI * 2); ctx.fill();
      }
    }

    size(); requestAnimationFrame(frame);
    window.addEventListener("resize", size);
  });
})();

// Earth–Moon CR3BP trajectory (precomputed Arenstorf orbit) animation
(function () {
  var cvs = document.querySelectorAll(".threebody");
  if (!cvs.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  cvs.forEach(function (cv) {
    fetch(cv.dataset.src).then(function (r) { return r.json(); }).then(function (d) {
      var ctx = cv.getContext("2d"), dpr = Math.min(Math.max((window.devicePixelRatio || 1) * 1.5, 2), 3);   // supersample for crisp lines
      var w, h, sc, ox, oy, pts = d.path, mu = d.mu, n = pts.length;
      function size() {
        w = cv.clientWidth; h = cv.clientHeight;
        cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        sc = Math.min(w / 3.0, h / 2.35); ox = w / 2 - 0.05 * sc; oy = h / 2;
      }
      function X(p) { return ox + p[0] * sc; }
      function Y(p) { return oy - p[1] * sc; }
      var stars = [];
      for (var i = 0; i < 90; i++) stars.push([Math.random(), Math.random(), Math.random()]);
      var t0 = performance.now(), period = 14000; // ms per orbit
      var orbit = null;

      function frame(now) {
        // rAF timestamps can be slightly earlier than t0 on the first frame -> clamp, never index < 0
        var el = Math.max(0, now - t0);
        var k = reduce ? n - 1 : Math.min(n - 1, Math.floor((el % period) / period * n));
        ctx.clearRect(0, 0, w, h);
                // full orbit (faint, cached)
        if (!orbit || orbit.sc !== sc) {
          orbit = new Path2D(); orbit.sc = sc;
          pts.forEach(function (p, i) { i ? orbit.lineTo(X(p), Y(p)) : orbit.moveTo(X(p), Y(p)); });
        }
        ctx.strokeStyle = "rgba(0,0,0,.15)"; ctx.lineWidth = 1; ctx.stroke(orbit);
        // trail drawn in chunks with increasing opacity / width
        var trail = Math.floor(n * 0.22), chunks = 40, step = Math.ceil(trail / chunks);
        ctx.lineCap = "round"; ctx.lineJoin = "round";
        for (var c = 0; c < chunks; c++) {
          var j0 = k - trail + c * step, j1 = Math.min(j0 + step + 1, k);
          if (j1 <= 0) continue;
          j0 = Math.max(0, j0);
          var a = (c + 1) / chunks;
          ctx.strokeStyle = "rgba(217,72,15," + (a * 0.95) + ")"; ctx.lineWidth = 0.8 + a * 2;
          ctx.beginPath(); ctx.moveTo(X(pts[j0]), Y(pts[j0]));
          for (var j = j0 + 1; j <= j1; j++) ctx.lineTo(X(pts[j]), Y(pts[j]));
          ctx.stroke();
        }
        // Lagrange points
        ctx.font = "italic 12px 'Times New Roman', serif";
        d.L.forEach(function (L, i) {
          var x = X(L), y = Y(L);
          ctx.strokeStyle = "#6741d9"; ctx.lineWidth = 1.3;
          ctx.beginPath(); ctx.moveTo(x - 4, y - 4); ctx.lineTo(x + 4, y + 4); ctx.moveTo(x + 4, y - 4); ctx.lineTo(x - 4, y + 4); ctx.stroke();
          ctx.fillStyle = "#6741d9"; ctx.fillText("L" + (i + 1), x + 6, y - 6);
        });
        // Earth
        var ex = X([-mu, 0]), ey = Y([-mu, 0]), er = Math.max(9, sc * 0.075);
        var g = ctx.createRadialGradient(ex - er * .4, ey - er * .4, er * .1, ex, ey, er);
        g.addColorStop(0, "#74a9ec"); g.addColorStop(1, "#2f5aa8");
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(ex, ey, er, 0, 7); ctx.fill();
        // Moon
        var mx = X([1 - mu, 0]), my = Y([1 - mu, 0]), mr = Math.max(4, er * 0.4);
        ctx.fillStyle = "#9aa1ab"; ctx.beginPath(); ctx.arc(mx, my, mr, 0, 7); ctx.fill();
        ctx.font = "13px Inter, sans-serif"; ctx.fillStyle = "#444";
        ctx.fillText("Earth", ex - 16, ey + er + 16); ctx.fillText("Moon", mx - 14, my + mr + 16);
        // spacecraft
        var p = pts[k]; ctx.fillStyle = "#222"; ctx.shadowColor = "rgba(217,72,15,.6)"; ctx.shadowBlur = 6;
        ctx.beginPath(); ctx.arc(X(p), Y(p), 3.2, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
        if (!reduce) requestAnimationFrame(frame);
      }
      size(); requestAnimationFrame(frame);
      window.addEventListener("resize", size);
    });
  });
})();

// research figures: click to enlarge
(function () {
  var box = document.querySelector(".fig-lightbox");
  if (!box) return;
  var img = box.querySelector("img");
  document.querySelectorAll(".research-fig img").forEach(function (im) {
    im.addEventListener("click", function () { img.src = im.src; img.alt = im.alt; box.hidden = false; });
  });
  box.addEventListener("click", function () { box.hidden = true; });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") box.hidden = true; });
})();

// publications: bold the journal / conference name inside each venue line
(function () {
  var re = /^((?:submitted to|accepted to)\s+)?(.+?)(?=,\s*(?:vol\.|pp\.|no\.|(?:Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sep|Oct|Nov|Dec)\b|\d{4})|$)/i;
  document.querySelectorAll(".pub-venue").forEach(function (el) {
    var t = el.textContent.trim();
    if (/^in preparation$/i.test(t)) return;
    var m = t.match(re);
    if (!m || !m[2]) return;
    var esc = function (s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;"); };
    el.innerHTML = esc(m[1] || "") + '<span class="venue-name">' + esc(m[2]) + "</span>" + esc(t.slice((m[1] || "").length + m[2].length));
  });
})();

// members: keep * only on the member's own name; keep all † when the member is an equal-contribution author
(function () {
  document.querySelectorAll(".member-pubs .pub-authors").forEach(function (el) {
    var nodes = Array.prototype.slice.call(el.childNodes);
    var afterOwn = function (node) {
      var prev = node.previousSibling;
      return prev && prev.nodeType === 1 && prev.classList.contains("lab");
    };
    var ownDagger = nodes.some(function (node) {
      return node.nodeType === 3 && afterOwn(node) && /^[*]*†/.test(node.nodeValue);
    });
    nodes.forEach(function (node) {
      if (node.nodeType !== 3) return;
      var t = node.nodeValue, keep = "";
      if (afterOwn(node)) {
        var m = t.match(/^[*†]+/);
        if (m) { keep = m[0]; t = t.slice(keep.length); }
      }
      node.nodeValue = keep + t.replace(ownDagger ? /[*]/g : /[*†]/g, "");
    });
  });
})();

// research canvases (constellation, three-body): click to enlarge the live animation
(function () {
  document.querySelectorAll(".research-fig .constellation-wrap").forEach(function (wrap) {
    var holder = null, back = null;
    function close() {
      wrap.classList.remove("zoomed");
      if (back) back.remove();
      if (holder) holder.replaceWith(wrap);
      back = holder = null;
      window.dispatchEvent(new Event("resize"));
    }
    wrap.addEventListener("click", function () {
      if (wrap.classList.contains("zoomed")) return close();
      holder = document.createElement("div");
      holder.style.height = wrap.offsetHeight + "px";
      wrap.parentNode.insertBefore(holder, wrap);
      document.body.appendChild(wrap);            // escape transformed ancestors so position:fixed is viewport-relative
      back = document.createElement("div");
      back.className = "canvas-backdrop";
      back.addEventListener("click", close);
      document.body.appendChild(back);
      wrap.classList.add("zoomed");
      window.dispatchEvent(new Event("resize"));
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && wrap.classList.contains("zoomed")) close(); });
  });
})();

// Earth-fixed beams (top-down view): 19 beams form a hexagonal lattice in the satellite's UV plane (u = sinθ cosφ, v = sinθ sinφ).
// The lattice is steered so the centre beam stays on a fixed ground point on the ground track; on the ground the cells stretch as the satellite moves away.
(function () {
  var cvs = document.querySelectorAll("canvas.efbeam");
  if (!cvs.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var beams = [];
  for (var q = -2; q <= 2; q++) for (var r = -2; r <= 2; r++) {
    if (Math.abs(q + r) > 2) continue;
    beams.push({ du: Math.sqrt(3) * (q + r / 2), dv: 1.5 * r, c: ((q - r) % 3 + 3) % 3, ring: Math.max(Math.abs(q), Math.abs(r), Math.abs(q + r)) });
  }
  var COL = [[76, 110, 245], [250, 82, 82], [18, 184, 134]];
  var H = 10, L = 7.5, RHO = 0.084, PERIOD = 8000;
  cvs.forEach(function (cv) {
    var ctx = cv.getContext("2d"), dpr = Math.min(Math.max((window.devicePixelRatio || 1) * 1.5, 2), 3);
    var w, h, s, cx, cy, t0 = performance.now();
    function size() {
      w = cv.clientWidth; h = cv.clientHeight;
      cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      s = Math.min(w / 19, h / 13); cx = w / 2; cy = h * 0.54;
    }
    function P(x, y) { return [cx + s * x, cy - s * y]; }
    function ground(S, u, v) {
      var n = Math.sqrt(Math.max(1e-4, 1 - u * u - v * v));
      return [S[0] + H * u / n, S[1] + H * v / n];
    }
    function poly(v) { ctx.beginPath(); v.forEach(function (p, i) { i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }); ctx.closePath(); }
    function drawSat(X, Y, k) {
      ctx.save(); ctx.translate(X, Y);
      ctx.shadowColor = "rgba(0,0,0,.25)"; ctx.shadowBlur = k * 0.5; ctx.shadowOffsetY = k * 0.25;
      var pw = k * 1.5, ph = k * 0.62;
      [-1, 1].forEach(function (sg) {
        var x0 = sg < 0 ? -k * 0.55 - pw : k * 0.55;
        var g = ctx.createLinearGradient(x0, -ph / 2, x0 + pw, ph / 2);
        g.addColorStop(0, "#1c3d8f"); g.addColorStop(1, "#3b6fd8");
        ctx.fillStyle = g; ctx.fillRect(x0, -ph / 2, pw, ph);
      });
      ctx.shadowColor = "transparent";
      [-1, 1].forEach(function (sg) {
        var x0 = sg < 0 ? -k * 0.55 - pw : k * 0.55;
        ctx.strokeStyle = "rgba(190,210,255,.8)"; ctx.lineWidth = 0.7;
        for (var j = 1; j < 6; j++) { ctx.beginPath(); ctx.moveTo(x0 + pw * j / 6, -ph / 2); ctx.lineTo(x0 + pw * j / 6, ph / 2); ctx.stroke(); }
        for (var j2 = 1; j2 < 3; j2++) { ctx.beginPath(); ctx.moveTo(x0, -ph / 2 + ph * j2 / 3); ctx.lineTo(x0 + pw, -ph / 2 + ph * j2 / 3); ctx.stroke(); }
        ctx.strokeStyle = "#0f2560"; ctx.lineWidth = 1; ctx.strokeRect(x0, -ph / 2, pw, ph);
        ctx.strokeStyle = "#6b7280"; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(sg * k * 0.4, 0); ctx.lineTo(sg * k * 0.55, 0); ctx.stroke();
      });
      var g2 = ctx.createLinearGradient(-k * 0.4, -k * 0.4, k * 0.4, k * 0.4);
      g2.addColorStop(0, "#f8f9fa"); g2.addColorStop(1, "#adb5bd");
      ctx.fillStyle = g2; ctx.strokeStyle = "#495057"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.rect(-k * 0.4, -k * 0.4, k * 0.8, k * 0.8); ctx.fill(); ctx.stroke();
      ctx.restore();
    }
    function frame(now) {
      var ph = reduce ? 0.5 : (Math.max(0, now - t0) % PERIOD) / PERIOD;
      var Sg = [-L + 2 * L * ph, 0];                          // sub-satellite point moves along the track through the centre beam
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, w, h);
      var dx = -Sg[0], dy = -Sg[1], R = Math.hypot(dx, dy, H), u0 = dx / R, v0 = dy / R;
      var foot = beams.map(function (b) {
        var uc = u0 + RHO * b.du, vc = v0 + RHO * b.dv, v = [];
        for (var i = 0; i < 24; i++) {                  // densely sampled edges so the stretched cells look smooth
          var e = Math.floor(i / 4), f = (i % 4) / 4;
          var a0 = Math.PI / 3 * e + Math.PI / 6, a1 = a0 + Math.PI / 3;
          var pu = (1 - f) * Math.cos(a0) + f * Math.cos(a1), pv = (1 - f) * Math.sin(a0) + f * Math.sin(a1);
          var g = ground(Sg, uc + RHO * pu, vc + RHO * pv);
          v.push(P(g[0], g[1]));
        }
        var gc = ground(Sg, uc, vc);
        return { b: b, v: v, c: P(gc[0], gc[1]) };
      });
      // ground track (travelled part solid)
      var t1 = P(-12, 0), t2 = P(12, 0), Sp = P(Sg[0], Sg[1]);
      ctx.strokeStyle = "rgba(73,80,87,.35)"; ctx.lineWidth = 1.5; ctx.setLineDash([7, 6]);
      ctx.beginPath(); ctx.moveTo(t1[0], t1[1]); ctx.lineTo(t2[0], t2[1]); ctx.stroke(); ctx.setLineDash([]);
      ctx.strokeStyle = "rgba(73,80,87,.75)"; ctx.lineWidth = 2.2;
      ctx.beginPath(); ctx.moveTo(t1[0], t1[1]); ctx.lineTo(Sp[0], Sp[1]); ctx.stroke();
      // cells
      foot.forEach(function (f) {
        var col = COL[f.b.c];
        var g = ctx.createRadialGradient(f.c[0], f.c[1], 0, f.c[0], f.c[1], s * 1.6);
        g.addColorStop(0, "rgba(" + col + ",.55)"); g.addColorStop(1, "rgba(" + col + ",.12)");
        poly(f.v); ctx.fillStyle = g; ctx.fill();
        ctx.strokeStyle = "#111"; ctx.lineWidth = 1; ctx.stroke();
      });
      // satellite -> beam centres
      foot.forEach(function (f) {
        ctx.strokeStyle = f.b.ring ? "rgba(33,37,41,.18)" : "rgba(224,49,49,.85)"; ctx.lineWidth = f.b.ring ? 0.8 : 2;
        ctx.beginPath(); ctx.moveTo(Sp[0], Sp[1]); ctx.lineTo(f.c[0], f.c[1]); ctx.stroke();
      });
      foot.forEach(function (f) {
        if (!f.b.ring) {
          var pulse = 1 + 0.35 * Math.sin(now / 250);
          ctx.strokeStyle = "rgba(224,49,49,.5)"; ctx.lineWidth = 1.5;
          ctx.beginPath(); ctx.arc(f.c[0], f.c[1], s * 0.35 * pulse, 0, 7); ctx.stroke();
          ctx.fillStyle = "#e03131"; ctx.beginPath(); ctx.arc(f.c[0], f.c[1], s * 0.16, 0, 7); ctx.fill();
          ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.5; ctx.stroke();
        } else {
          ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(f.c[0], f.c[1], s * 0.09, 0, 7); ctx.fill();
          ctx.strokeStyle = "#343a40"; ctx.lineWidth = 1.2; ctx.stroke();
        }
      });
      drawSat(Sp[0], Sp[1], s * 0.85);
      var th = Math.acos(H / R) * 180 / Math.PI, f = Math.max(11, w / 42);
      ctx.font = "700 " + (f * 1.1) + "px Inter, sans-serif"; ctx.fillStyle = "#212529";
      ctx.fillText("Off-nadir steering  " + th.toFixed(0) + "°", f, f * 1.7);
      // elevation of the satellite seen from the centre-beam point (spherical Earth; H = 600 km -> R_E = 6371 km in scene units)
      var RE = H * 6371 / 600, el = Math.acos(Math.min(1, (RE + H) / RE * Math.sin(th * Math.PI / 180))) * 180 / Math.PI;
      ctx.fillText("Centre-beam elevation  " + el.toFixed(0) + "°", f, f * 3.1);
      ctx.font = "500 " + (f * 0.85) + "px Inter, sans-serif"; ctx.fillStyle = "#495057";
      ctx.fillText("Hexagonal in the UV plane → stretched on the ground", f, f * 4.4);
      var ly = h - f * 1.1;
      ctx.fillStyle = "#e03131"; ctx.beginPath(); ctx.arc(f * 1.3, ly - f * 0.3, f * 0.3, 0, 7); ctx.fill();
      ctx.fillStyle = "#212529"; ctx.fillText("Earth-fixed centre beam", f * 2, ly);
      ctx.fillStyle = "#fff"; ctx.strokeStyle = "#343a40"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.arc(f * 13.6, ly - f * 0.3, f * 0.22, 0, 7); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#212529"; ctx.fillText("Beam centres", f * 14.2, ly);
      ctx.strokeStyle = "rgba(73,80,87,.75)"; ctx.lineWidth = 2.2; ctx.beginPath(); ctx.moveTo(f * 21, ly - f * 0.3); ctx.lineTo(f * 22.6, ly - f * 0.3); ctx.stroke();
      ctx.fillStyle = "#212529"; ctx.fillText("Ground track", f * 23, ly);
      requestAnimationFrame(frame);
    }
    size(); window.addEventListener("resize", size);
    requestAnimationFrame(frame);
  });
})();
