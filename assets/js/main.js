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

  // Gallery lightbox
  var lb = document.querySelector(".lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img"), lbCap = lb.querySelector("p");
    document.querySelectorAll(".gallery-open").forEach(function (b) {
      b.addEventListener("click", function () {
        lbImg.src = b.dataset.src; lbImg.alt = b.dataset.caption; lbCap.textContent = b.dataset.caption;
        lb.hidden = false;
      });
    });
    function close() { lb.hidden = true; }
    lb.addEventListener("click", function (e) { if (e.target !== lbImg) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
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
    var w, h, R, cx, cy, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var t0 = performance.now();

    function size() {
      w = cv.clientWidth; h = cv.clientHeight;
      cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      R = Math.min(w, h) * 0.34; cx = w / 2; cy = h / 2;
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

      // satellites positions
      var pts = [];
      for (var p = 0; p < P; p++) {
        pts[p] = [];
        for (var k = 0; k < S; k++) { var q = satPos(p, k, orbitT); pts[p][k] = proj(q[0], q[1], q[2], spin); }
      }

      // back-side sats & links (behind earth)
      drawLayer(pts, false);

      // earth
      var g = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R);
      g.addColorStop(0, "#3d7fd6"); g.addColorStop(0.6, "#1b3f8a"); g.addColorStop(1, "#0a1836");
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
      // graticule
      ctx.strokeStyle = "rgba(160,200,255,.16)"; ctx.lineWidth = 0.7;
      for (var lat = -75; lat <= 75; lat += 15) drawCircle(function (a) {
        return [Math.cos(lat * D2R) * Math.cos(a), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.sin(a)];
      }, spin);
      for (var lon = 0; lon < 180; lon += 15) drawCircle(function (a) {
        return [Math.cos(a) * Math.cos(lon * D2R), Math.sin(a), Math.cos(a) * Math.sin(lon * D2R)];
      }, spin);
      // atmosphere rim
      ctx.beginPath(); ctx.arc(cx, cy, R + 2, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(127,211,255,.55)"; ctx.lineWidth = 2; ctx.stroke();

      // front-side sats & links
      drawLayer(pts, true);
      if (!reduce) requestAnimationFrame(frame);
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
        ctx.fillStyle = front ? "#e8f6ff" : "rgba(232,246,255,.35)";
        ctx.beginPath(); ctx.arc(s[0], s[1], front ? 1.8 : 1.2, 0, Math.PI * 2); ctx.fill();
      }
    }

    size(); requestAnimationFrame(frame);
    window.addEventListener("resize", size);
  });
})();
