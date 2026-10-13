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
      // atmosphere rim
      ctx.beginPath(); ctx.arc(cx, cy, R + 2, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(47,90,168,.6)"; ctx.lineWidth = 1.5; ctx.stroke();

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
      var ctx = cv.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w, h, sc, ox, oy, pts = d.path, mu = d.mu, n = pts.length;
      function size() {
        w = cv.clientWidth; h = cv.clientHeight;
        cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        sc = Math.min(w / 3.0, h / 2.7); ox = w / 2 - 0.05 * sc; oy = h / 2;
      }
      function X(p) { return ox + p[0] * sc; }
      function Y(p) { return oy - p[1] * sc; }
      var stars = [];
      for (var i = 0; i < 90; i++) stars.push([Math.random(), Math.random(), Math.random()]);
      var t0 = performance.now(), period = 14000; // ms per orbit

      function frame(now) {
        var k = reduce ? n - 1 : Math.floor(((now - t0) % period) / period * n);
        ctx.clearRect(0, 0, w, h);
                // full orbit (faint)
        ctx.strokeStyle = "rgba(0,0,0,.15)"; ctx.lineWidth = 1;
        ctx.beginPath(); pts.forEach(function (p, i) { i ? ctx.lineTo(X(p), Y(p)) : ctx.moveTo(X(p), Y(p)); }); ctx.stroke();
        // trail
        var trail = Math.floor(n * 0.22);
        for (var j = Math.max(1, k - trail); j <= k; j++) {
          var a = (j - (k - trail)) / trail;
          ctx.strokeStyle = "rgba(217,72,15," + (a * 0.95) + ")"; ctx.lineWidth = 0.8 + a * 2;
          ctx.beginPath(); ctx.moveTo(X(pts[j - 1]), Y(pts[j - 1])); ctx.lineTo(X(pts[j]), Y(pts[j])); ctx.stroke();
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
