// Render storyboard key frames (1080x1920) for V1/V2 and one review sheet per version.
// Usage: NODE_PATH=<global node_modules> node render.js <repo_root>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const root = process.argv[2];
const out = path.join(root, 'renders', 'storyboard');
const scenes = require('./scenes.js');
const tr = JSON.parse(fs.readFileSync(path.join(root, 'analysis', 'transcript.json'), 'utf8'));
const phr = Object.fromEntries(tr.phrases.map((p) => [p.id, p]));

// every on-screen text must be a piece of the scene's spoken phrases
const norm = (s) => s.replace(/\[\[|\]\]|\{\{|\}\}/g, '').replace(/[\s،,!؟?…«».:]/g, '');
for (const sc of scenes) {
  const spoken = norm(sc.phrases.map((i) => phr[i].screen_text).join(' '));
  const texts = [sc.cap, sc.kw, sc.cta, sc.v1 && sc.v1.bubble, sc.v1 && sc.v1.strip, sc.v1 && sc.v1.stamp,
    sc.v2 && sc.v2.stamp, ...((sc.v2 && sc.v2.lines) || []).map((l) => l.t),
    ...[...(sc.extras || []), ...(sc.extrasV1 || []), ...(sc.extrasV2 || [])].filter((e) => e.type === 'big').map((e) => e.t)]
    .filter(Boolean);
  for (const t of texts) {
    if (!spoken.includes(norm(t))) throw new Error(`${sc.id}: on-screen text not in spoken phrases: ${t}`);
  }
}

(async () => {
  fs.copyFileSync(path.join(__dirname, 'template.html'), path.join(out, 'index.html'));
  fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(out, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  for (const v of ['V1', 'V2']) {
    for (const sc of scenes) {
      await page.evaluate(([s, ver]) => window.render(s, ver, { safe: true }), [sc, v]);
      await page.evaluate(() => Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: path.join(out, 'frames', `${v}_${sc.id}.png`) });
    }
  }

  // review sheets
  const esc = (s) => s.replace(/\[\[|\]\]|\{\{|\}\}/g, '');
  for (const v of ['V1', 'V2']) {
    const cards = scenes.map((sc) => {
      const said = sc.phrases.map((i) => `${phr[i].screen_text}${phr[i].screen_text_status === 'question_open' ? ' (؟)' : ''}`).join(' ');
      return `<div class="card"><img src="frames/${v}_${sc.id}.png">
        <div class="meta"><b>${sc.id}</b><span dir="ltr">${sc.t[0].toFixed(2)}–${sc.t[1].toFixed(2)} s</span></div>
        <div class="said">${said ? '«' + esc(said) + '»' : '(صمت)'}</div>
        <div class="beat">${sc.beats[v]}</div><div class="assets">${sc.assets}</div></div>`;
    }).join('\n');
    const title = v === 'V1' ? 'النسخة 1 — بشخصية البكسل' : 'النسخة 2 — بدون شخصية';
    const html = `<!doctype html><html dir="rtl"><head><meta charset="utf-8"><style>
      @font-face{font-family:Cairo;src:url(assets/Cairo.ttf);font-weight:200 1000}
      body{margin:0;background:#120D2E;color:#fff;font-family:Cairo;padding:48px 40px;width:2280px;box-sizing:border-box}
      h1{font-size:56px;margin:0 0 8px} p.sub{font-size:28px;color:#C9C0FF;margin:0 0 36px;line-height:1.5}
      .grid{display:grid;grid-template-columns:repeat(5,1fr);gap:36px 28px}
      .card{background:#1E1650;border-radius:18px;padding:14px;box-shadow:0 0 0 2px #3A2D8C}
      .card img{width:100%;border-radius:10px;display:block}
      .meta{display:flex;justify-content:space-between;align-items:center;margin:12px 4px 6px;font-size:30px}
      .meta b{color:#F2A60F} .meta span{font-size:24px;color:#C9C0FF}
      .said{font-size:25px;font-weight:800;line-height:1.5;margin:0 4px 8px}
      .beat{font-size:22px;line-height:1.55;color:#E4DEFF;margin:0 4px 8px}
      .assets{font-size:22px;font-weight:700;color:#F2A60F;margin:0 4px}
    </style></head><body><h1>لوحة المشاهد الثابتة — ${title}</h1>
    <p class="sub">إطار مفتاحي واحد لكل مشهد على التوقيت المقاس، والصوت هو التسجيل الأصلي دون تغيير. الشاشات الحقيقية من لقطاتك وتسجيلك. المربعات المقطّعة أماكن شاشات ناقصة. المساحات المخططة هي منطقة واجهة تيك توك وإنستقرام (لا نص مهم فيها). (؟) = صياغة بانتظار تأكيدك. هذه لوحة مراجعة وليست الفيديو النهائي.</p>
    <div class="grid">${cards}</div></body></html>`;
    fs.writeFileSync(path.join(out, `sheet_${v}.html`), html);
    const sp = await browser.newPage({ viewport: { width: 2280, height: 1200 } });
    await sp.goto('file://' + path.join(out, `sheet_${v}.html`));
    await sp.evaluate(() => document.fonts.ready);
    await sp.evaluate(() => Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
    await sp.screenshot({ path: path.join(out, `storyboard_${v}.png`), fullPage: true });
    await sp.close();
  }
  await browser.close();
  console.log('done');
})().catch((e) => { console.error(e); process.exit(1); });
