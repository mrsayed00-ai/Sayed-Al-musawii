// Frame renderer for the animated previews. Loaded into the page together with
// the storyboard CSS; window.renderFrame(i) draws frame i of version VERSION.
/* global DATA */
(() => {
  const $ = (h) => { const t = document.createElement('template'); t.innerHTML = h.trim(); return t.content.firstChild; };
  const latin = (s) => s.replace(/[A-Za-z][A-Za-z .]*[A-Za-z]/g, (m) => `<bdi dir="ltr" style="white-space:nowrap">${m}</bdi>`);
  const hl = (s) => latin(s).replace(/\[\[(.+?)\]\]/g, '<span class="hl">$1</span>').replace(/\{\{(.+?)\}\}/g, '<span class="hlp">$1</span>');
  const clamp = (x) => Math.max(0, Math.min(1, x));
  const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const easeBack = (x) => { x = clamp(x); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const enter = (t, t0, dur = 0.35, dy = 50) => {
    const p = easeBack((t - t0) / dur), o = clamp((t - t0) / (dur * 0.6));
    return `opacity:${o};transform:translateY(${(1 - p) * dy}px) scale(${0.92 + 0.08 * p})`;
  };
  const pop = (t, t0, dur = 0.2) => `opacity:${clamp((t - t0) / (dur * 0.7))};transform:scale(${0.9 + 0.1 * easeBack((t - t0) / dur)})`;

  function phraseAt(t, sc) {
    let cur = null;
    for (const p of DATA.phrases) if (p.start <= t + 1e-6 && p.start >= sc.start - 0.05 && p.start < sc.end) cur = p;
    return cur;
  }

  function device(d, t, sc, V1) {
    const [x, y, w, h] = d.box;
    const t0 = d.appear != null ? d.appear : sc.start;
    if (t < t0) return null;
    let style = enter(t, t0);
    if (d.shake && t >= d.shake[0] && t <= d.shake[1]) {
      const k = Math.floor(t * 30);
      style += `;translate:${(hash(k) - 0.5) * 8}px ${(hash(k + 7) - 0.5) * 6}px`;
    }
    const el = $(`<div class="device ${d.kind}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;${style}"></div>`);
    const kb = 1 + 0.03 * clamp((t - sc.start) / (sc.end - sc.start));
    const layer = (src, o) => `<img src="assets/${src}" style="position:absolute;inset:14px;width:calc(100% - 28px);height:calc(100% - 28px);object-fit:cover;object-position:${d.pos || 'center'};opacity:${o};transform:scale(${kb})">`;
    if (d.seq) {
      let cur = 0;
      d.seq.forEach((s, k) => { if (t >= s[0]) cur = k; });
      if (cur > 0) {
        const fade = clamp((t - d.seq[cur][0]) / 0.18);
        if (fade < 1) el.appendChild($(layer(d.seq[cur - 1][1], 1)));
        el.appendChild($(layer(d.seq[cur][1], fade)));
      } else el.appendChild($(layer(d.seq[0][1], 1)));
    } else el.appendChild($(layer(d.img, 1)));
    el.style.overflow = 'hidden';
    return el;
  }

  function character(f, key, size, sceneId) {
    let scale, left, top, tall = false;
    if (size === 'small') { scale = 7; left = 40 - 12 * scale; top = 1020; }
    else if (sceneId === 'S19') { scale = 10; left = 540 - 36 * scale; top = 1010; tall = true; }
    else if (sceneId === 'S20') { scale = 10; left = 540 - 36 * scale; top = 960; tall = true; }
    else { scale = 13; left = 540 - 36 * scale; top = 760; tall = true; }
    const w = 72 * scale, h = (tall ? 100 : 60) * scale;
    f.appendChild($(`<img class="char" src="assets/charv/${key}${tall ? '_tall' : ''}.png" style="left:${left}px;top:${top}px;width:${w}px;height:${h}px">`));
  }

  function pixels(f, t) {
    let cov = t < 0.6 ? 1 - t / 0.6 : 0;
    for (const c of DATA.cuts) { const d = Math.abs(t - c); if (d < 0.3) cov = Math.max(cov, 1 - d / 0.3); }
    if (cov <= 0) return;
    const S = 90, cols = 12, rows = 22, colors = ['#FFFFFF', '#B2A4FF', '#7F71CE', '#5230BB'];
    let html = '';
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const n = r * cols + c;
      if (hash(n) < cov) html += `<div style="position:absolute;left:${c * S}px;top:${r * S}px;width:${S}px;height:${S}px;background:${colors[Math.floor(hash(n + 999) * 4)]}"></div>`;
    }
    f.appendChild($(`<div style="position:absolute;inset:0">${html}</div>`));
  }

  window.renderFrame = (i) => {
    const V1 = DATA.version === 'V1';
    const t = i / DATA.fps;
    const fr = DATA.frames[i];
    const win = DATA.sceneWin[fr.scene];
    const sc = { ...DATA.sceneSpec[fr.scene], start: win.start, end: win.end };
    const f = document.getElementById('f');
    f.innerHTML = '';
    f.appendChild($('<div class="bg"></div>'));
    const bgs = V1 ? sc.bgshotV1 : sc.bgshot;
    if (bgs) { f.appendChild($(`<div class="bgshot" style="background-image:url(assets/${bgs})"></div>`)); f.appendChild($('<div class="tint"></div>')); }
    const g = sc.glow || [540, 900];
    const pulse = 1 + 0.04 * Math.sin(t * 2.1);
    f.appendChild($(`<div class="glow" style="right:${1080 - g[0]}px;top:${g[1]}px;transform:translate(50%,-50%) scale(${pulse})"></div>`));
    f.appendChild($('<div class="dither"></div>'));
    if (sc.redwash) f.appendChild($('<div class="redwash"></div>'));
    if (sc.redflash != null && t >= sc.redflash) {
      const a = Math.max(0, 0.65 - (t - sc.redflash) / 0.4 * 0.65);
      if (a > 0) f.appendChild($(`<div style="position:absolute;inset:0;background:rgba(229,58,52,${a})"></div>`));
    }
    const ph = phraseAt(t, sc);

    if (sc.heading) {
      f.appendChild($(`<div class="heading" style="${enter(t, sc.start, 0.3, -40)}"><h1>${latin(sc.heading.text)}</h1><span class="step" style="background:${sc.heading.color || 'var(--yellow)'};color:${sc.heading.ink || 'var(--ink)'}">${sc.heading.step}</span></div>`));
    }

    if (sc.layout === 'hook') {
      const k = V1 ? sc.v1 : sc.v2;
      if (V1) {
        if (k.bubble) {
          const t0 = sc.id === 'S02' ? sc.start : -1;
          f.appendChild($(`<div class="bubble" style="${t0 >= 0 ? pop(t, t0, 0.25) : ''}">${hl(k.bubble)}</div>`));
        }
        if (k.strip) f.appendChild($(`<div class="strip" style="top:${k.stripTop || 560}px;${enter(t, sc.start, 0.3, 30)}">${hl(k.strip)}</div>`));
        if (k.stamp) {
          const p = clamp((t - sc.start) / 0.15), j = t - sc.start < 0.3 ? (hash(Math.floor(t * 30)) - 0.5) * 14 : 0;
          f.appendChild($(`<div class="stamp" style="top:${k.stampTop || 330}px;opacity:${p};transform:rotate(-4deg) scale(${1.6 - 0.6 * p}) translateX(${j}px)">${k.stamp}</div>`));
        }
      } else {
        (k.lines || []).forEach((ln, n) => f.appendChild($(`<div class="big ${ln.dim ? 'dim' : ''}" style="top:${ln.top}px;${ln.dim ? '' : enter(t, sc.start + n * 0.12, 0.3, 40)}">${hl(ln.t)}</div>`)));
        if (k.stamp) {
          const p = clamp((t - sc.start) / 0.15), j = t - sc.start < 0.3 ? (hash(Math.floor(t * 30)) - 0.5) * 14 : 0;
          f.appendChild($(`<div class="stamp" style="top:${k.stampTop || 760}px;opacity:${p};transform:rotate(-4deg) scale(${1.6 - 0.6 * p}) translateX(${j}px)">${k.stamp}</div>`));
        }
        if (k.logo) f.appendChild($(`<img class="logo" src="assets/fanous_wordmark_white.png" style="top:${k.logo.top}px;width:${k.logo.w}px;opacity:${clamp(t / 0.4)}">`));
      }
    }

    if (sc.layout === 'stage') {
      const st = V1 ? (sc.stageV1 || sc.stage) : sc.stage;
      for (const d of st) { const el = device(d, t, sc, V1); if (el) f.appendChild(el); }
      const extras = (V1 ? sc.extrasV1 : sc.extrasV2) || sc.extras || [];
      for (const e of extras) {
        if (e.type === 'big' && ph) f.appendChild($(`<div class="big ${e.cls || ''}" style="top:${e.top}px;font-size:${e.size || 130}px;${pop(t, ph.start, 0.22)}">${hl(e.t)}</div>`));
        if (e.type === 'chip') {
          const t0 = sc.start + 0.25 + (e.t === 'لا' ? 0.6 : 0);
          const out = sc.chipsUntil && t > sc.chipsUntil ? clamp(1 - (t - sc.chipsUntil) / 0.2) : 1;
          if (t >= t0 && out > 0) f.appendChild($(`<div class="chip" style="left:${e.x}px;top:${e.y}px;background:${e.bg};opacity:${clamp((t - t0) / 0.12) * out};transform:rotate(${(e.rot || 0) + Math.sin(t * 6 + e.x) * 3}deg) scale(${0.85 + 0.15 * easeBack((t - t0) / 0.25)})">${e.t}</div>`));
        }
        if (e.type === 'blind') {
          const W = 64 * e.scale, H = 40 * e.scale, k = Math.floor(t * 8) % 8;
          const bob = (ph) => 2.5 * Math.sin(2 * Math.PI * t / 1.4 + ph);
          const lay = (src, dy) => `<img src="assets/blind/${src}" style="position:absolute;left:0;top:0;width:${W}px;height:${H}px;image-rendering:pixelated;transform:translateY(${dy}px)">`;
          f.appendChild($(`<div style="position:absolute;left:${e.x}px;top:${e.y}px;width:${W}px;height:${H}px;opacity:${clamp((t - sc.start - 0.3) / 0.35)}">${lay('playerA.png', bob(0))}${lay('playerB.png', bob(Math.PI))}${lay(`fx_${k}.png`, 0)}</div>`));
        }
        if (e.type === 'illus') f.appendChild($(`<div class="illus" style="left:${e.x}px;top:${e.y}px;transform:scale(${e.scale || 1});transform-origin:top left;opacity:${clamp((t - sc.start - 0.4) / 0.3)}">${e.html}</div>`));
      }
      if (sc.meter) {
        const fill = 70 * clamp((t - sc.meter.from) / (sc.meter.to - sc.meter.from));
        const mx = V1 ? 486 : 350;
        f.appendChild($(`<div class="meter" style="left:${mx}px;top:1080px;${enter(t, sc.start + 0.3, 0.3, 20)}"><b>الشك</b><i style="width:${fill}%"></i></div>`));
      }
      if (ph && DATA.captions[ph.id]) {
        const [c2, c1] = DATA.captions[ph.id];
        if (V1 && c1) f.appendChild($(`<div class="kw" style="${pop(t, ph.start)}">${hl(c1)}</div>`));
        if (!V1 && c2) f.appendChild($(`<div class="cap" style="${pop(t, ph.start)}"><div>${hl(c2)}</div></div>`));
      }
    }

    if (sc.layout === 'tiles') {
      sc.tiles.forEach((tl, n) => {
        const [x, y, w, h] = V1 ? tl.boxV1 : tl.box;
        const t0 = sc.start + 0.1 + n * 0.12;
        if (t >= t0) f.appendChild($(`<div class="tile" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;${enter(t, t0, 0.35, 40)}"><img src="assets/${tl.img}" style="object-position:${tl.pos || 'center'}"><em>${latin(tl.label)}</em></div>`));
      });
      if (ph && DATA.captions[ph.id]) {
        const [c2, c1] = DATA.captions[ph.id];
        if (V1) f.appendChild($(`<div class="bubble" style="top:250px;font-size:60px;${pop(t, ph.start, 0.25)}">${hl(c1)}</div>`));
        else f.appendChild($(`<div class="cap" style="${pop(t, ph.start)}"><div>${hl(c2)}</div></div>`));
      }
    }

    if (sc.layout === 'end') {
      const lt = sc.start;
      f.appendChild($(`<img class="logo" src="assets/fanous_wordmark_white.png" style="top:${V1 ? 300 : 420}px;width:${V1 ? 640 : 780}px;opacity:${clamp((t - lt) / 0.2)};transform:translateX(-50%) scale(${0.6 + 0.4 * easeBack((t - lt) / 0.4)})">`));
      if (t >= lt + 0.25) f.appendChild($(`<div class="big" style="top:${V1 ? 560 : 760}px;font-size:104px;${enter(t, lt + 0.25, 0.3, 30)}">${hl(sc.cta)}</div>`));
      if (t >= lt + 0.6) {
        const b = 1 + 0.04 * Math.sin((t - lt) * 5) * clamp((t - lt - 0.9) / 0.3);
        f.appendChild($(`<div class="url" style="top:${V1 ? 730 : 960}px;opacity:${clamp((t - lt - 0.6) / 0.15)};transform:translateX(-50%) scale(${(0.7 + 0.3 * easeBack((t - lt - 0.6) / 0.35)) * b})">alfanous.app</div>`));
      }
    }

    if (V1) character(f, fr.char, fr.size, fr.scene);
    pixels(f, t);
  };
})();
