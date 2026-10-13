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
