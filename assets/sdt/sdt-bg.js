/* Background layer for open3dcp.org: a calm mosaic of many small datasets, each filling with
   records row by row while the whole field drifts slowly.
   Reads <html data-sdt-bg="collection|plain"> and draws a decorative, aria-hidden canvas behind
   the page. One animation loop at up to 30 fps, paused in hidden tabs, device pixel ratio capped
   at 2, fainter under 720 px, and a still frame under prefers-reduced-motion. Records are drawn
   as small squares batched by colour, a few fills per frame. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var STILL = 21;            // seconds into the motion shown as the still frame
  var FRAME_MS = 1000 / 30;
  var layer = null;
  var stop = function () {};

  function hash(a, b) {
    var s = Math.sin(a * 127.1 + b * 311.7 + 74.7) * 43758.5453;
    return s - Math.floor(s);
  }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  // Calmer on the left, where page text usually sits. Phones are uniformly faint instead.
  function side(x, w, small) { return small ? 0.62 : 0.3 + 0.7 * clamp((x / w - 0.18) / 0.5); }
  function q(a) { return (Math.round(clamp(a) * 25) / 25).toFixed(2); }
  function steel(a) { return "rgba(169,203,239," + q(a) + ")"; }
  function pale(a) { return "rgba(194,212,224," + q(a) + ")"; }
  function lime(a) { return "rgba(151,215,0," + q(a) + ")"; }

  /* Rectangles grouped by colour; alpha is quantised so there are only a few groups. */
  function Batch() { this.groups = {}; }
  Batch.prototype.add = function (style, x, y, rw, rh) {
    (this.groups[style] || (this.groups[style] = [])).push(x, y, rw, rh === undefined ? rw : rh);
  };
  Batch.prototype.flush = function (ctx) {
    for (var style in this.groups) {
      var a = this.groups[style];
      ctx.fillStyle = style;
      ctx.beginPath();
      for (var i = 0; i < a.length; i += 4) ctx.rect(a[i], a[i + 1], a[i + 2], a[i + 3]);
      ctx.fill();
    }
    this.groups = {};
  };

  /* The field is a lattice of tiles; about 70% hold a small table of 4-12 columns by 3-8 rows.
     Each table gains rows at its own pace, holds briefly, fades and starts again. A few cells of
     the newest row glint in the site's lime. */
  function collection(ctx, w, h, t, small, batch) {
    var sx = small ? 118 : 134, sy = small ? 94 : 98, pitch = 6, size = small ? 1.6 : 1.5;
    var panX = t * 5, panY = t * 2.2;
    var i0 = Math.floor(panX / sx) - 1, j0 = Math.floor(panY / sy) - 1;
    var ni = Math.ceil(w / sx) + 3, nj = Math.ceil(h / sy) + 3;
    var dim = small ? 0.72 : 1;
    for (var j = j0; j < j0 + nj; j++) {
      for (var i = i0; i < i0 + ni; i++) {
        if (hash(i, j) < 0.3) continue;
        var nc = 4 + Math.floor(hash(i, j + 0.5) * 9), nr = 3 + Math.floor(hash(i + 0.5, j) * 6);
        var ox = i * sx - panX + hash(i, j + 3) * (sx - nc * pitch - 10);
        var oy = j * sy - panY + hash(i + 3, j) * (sy - nr * pitch - 12);
        if (ox > w || oy > h || ox + nc * pitch < 0 || oy + nr * pitch < 0) continue;
        var cyc = nr + 5, rate = 0.3 + hash(i + 7, j) * 0.45;
        var prog = (t * rate + hash(i, j + 9) * cyc) % cyc;
        var filled = Math.min(nr, prog);
        var fade = prog > nr + 3 ? 1 - (prog - nr - 3) / 2 : 1;
        var wgt = side(ox, w, small) * dim * fade;
        batch.add(steel(0.2 * wgt), ox - 1, oy - 4, nc * pitch, 1);   // header rule
        var whole = Math.floor(filled), part = filled - whole;
        for (var rr = 0; rr < Math.ceil(filled); rr++) {
          var newest = rr === whole && part > 0, k = newest ? part : 1;
          for (var cc = 0; cc < nc; cc++) {
            if (newest && cc / nc > k) break;
            if (hash(i * 31 + cc, j * 17 + rr) < 0.16) continue;   // empty values stay empty
            var x = ox + cc * pitch, y = oy + rr * pitch;
            if (newest && hash(i + cc, j + rr * 3) < 0.12) batch.add(lime(0.75 * wgt), x, y, size);
            else batch.add(newest ? pale(0.55 * wgt) : steel(0.3 * wgt), x, y, size);
          }
        }
      }
    }
  }

  var MODES = { collection: collection };

  function draw(mode, ctx, w, h, t) {
    var batch = new Batch();
    MODES[mode](ctx, w, h, t, w < 720, batch);
    batch.flush(ctx);
  }

  function run(host, mode) {
    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext("2d");
    var w = 0, h = 0, id = 0, last = 0, t = 0, drawn = 0;
    host.appendChild(canvas);
    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function paint() {
      ctx.clearRect(0, 0, w, h);
      draw(mode, ctx, w, h, reduced.matches ? STILL : STILL + t);
    }
    function tick(now) {
      id = 0;
      if (reduced.matches || document.hidden) return;
      id = requestAnimationFrame(tick);
      if (now - drawn < FRAME_MS) return;
      t += last ? Math.min((now - last) / 1000, 0.1) : 0;
      last = now;
      drawn = now;
      paint();
    }
    function start() {
      cancelAnimationFrame(id);
      id = 0;
      last = 0;
      resize();
      paint();
      if (!reduced.matches && !document.hidden) id = requestAnimationFrame(tick);
    }
    function onVisible() { if (!document.hidden) start(); }
    window.addEventListener("resize", start);
    document.addEventListener("visibilitychange", onVisible);
    reduced.addEventListener("change", start);
    start();
    return function () {
      cancelAnimationFrame(id);
      window.removeEventListener("resize", start);
      document.removeEventListener("visibilitychange", onVisible);
      reduced.removeEventListener("change", start);
    };
  }

  function mount(mode) {
    stop();
    stop = function () {};
    if (layer) layer.remove();
    layer = null;
    if (root.getAttribute("data-sdt-theme") !== "dark" || !MODES[mode]) return;
    layer = document.createElement("div");
    layer.className = "sdt-bg sdt-bg--" + mode;
    layer.setAttribute("aria-hidden", "true");
    document.body.insertBefore(layer, document.body.firstChild);
    stop = run(layer, mode);
  }

  window.sdtBg = {
    set: function (mode) { root.setAttribute("data-sdt-bg", mode); mount(mode); },
    frame: function (mode, ctx, w, h, t) { draw(mode, ctx, w, h, t); }
  };
  mount(root.getAttribute("data-sdt-bg"));
})();
