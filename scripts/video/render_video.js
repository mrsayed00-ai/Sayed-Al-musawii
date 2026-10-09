// Render the animated previews (V1 + V2) frame by frame with Playwright, then
// mux with the voice using ffmpeg.
// Usage: NODE_PATH=<global node_modules> node render_video.js <repo_root> [--test t1,t2,...] [--scale 0.5] [--audio <wav>] [--only V1|V2] [--encode-only]
// --scale 1 writes the 1080x1920 export to renders/final/, smaller scales write previews to renders/video/.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const root = process.argv[2];
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const testTimes = arg('--test', null);
const scale = parseFloat(arg('--scale', '0.5'));
const audio = arg('--audio', path.join(root, 'media', 'derived', 'voice2_enhanced.wav'));
const only = arg('--only', null);
const encodeOnly = process.argv.includes('--encode-only'); // reuse captured frames, re-run ffmpeg only
const FULL = scale === 1;
const out = path.join(root, 'renders', 'video');
const sbDir = path.join(root, 'renders', 'storyboard');
const tl = JSON.parse(fs.readFileSync(path.join(out, 'timeline.json'), 'utf8'));
const tr = JSON.parse(fs.readFileSync(path.join(root, 'analysis', 'transcript.json'), 'utf8'));
const { scenes, CAPTIONS } = require('./video_scenes.js');

// captions: V2 must equal the spoken screen_text; V1 keyword must be a piece of it
const strip = (s) => s.replace(/\[\[|\]\]|\{\{|\}\}/g, '');
const norm = (s) => strip(s).replace(/[\s،,!؟?…«».:]/g, '');
for (const p of tr.phrases) {
  const c = CAPTIONS[p.id];
  if (!c) continue;
  if (c[0] && strip(c[0]) !== p.screen_text) throw new Error(`caption ${p.id} differs from screen_text:\n${strip(c[0])}\n${p.screen_text}`);
  if (c[1] && !norm(p.screen_text).includes(norm(c[1]))) throw new Error(`keyword ${p.id} not in phrase: ${c[1]}`);
}

const css = fs.readFileSync(path.join(__dirname, '..', 'storyboard', 'template.html'), 'utf8').match(/<style>([\s\S]*?)<\/style>/)[1];
const anim = fs.readFileSync(path.join(__dirname, 'anim.js'), 'utf8');

(async () => {
  const browser = await chromium.launch();
  const issues = [];
  for (const version of ['V1', 'V2'].filter((v) => !only || v === only)) {
    const data = {
      version, fps: tl.fps, frames: tl.frames, cuts: tl.cuts, phrases: tl.phrases, captions: CAPTIONS,
      sceneWin: Object.fromEntries(tl.scenes.map((s) => [s.id, s])),
      sceneSpec: Object.fromEntries(scenes.map((s) => [s.id, s])),
    };
    const html = `<!doctype html><html dir="rtl" lang="ar"><head><meta charset="utf-8"><style>${css}</style></head>
      <body><div id="f"></div><script>window.DATA=${JSON.stringify(data)};</script><script>${anim}</script></body></html>`;
    const page_file = path.join(sbDir, `anim_${version}.html`);
    fs.writeFileSync(page_file, html);
    const frames = testTimes ? testTimes.split(',').map((s) => Math.round(parseFloat(s) * tl.fps)) : [...Array(tl.n).keys()];
    const dir = path.join(out, testTimes ? `test_${version}` : `frames_${version}`);
    if (!encodeOnly) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: scale });
    await page.goto('file://' + page_file);
    await page.evaluate(() => document.fonts.ready);
    fs.rmSync(dir, { recursive: true, force: true });
    fs.mkdirSync(dir, { recursive: true });
    for (const i of frames) {
      await page.evaluate((k) => window.renderFrame(k), i);
      await page.evaluate(() => Promise.all([...document.images].map((im) => im.complete ? 0 : new Promise((r) => { im.onload = im.onerror = r; }))));
      const name = testTimes ? `t${(i / tl.fps).toFixed(2)}.jpg` : `f${String(i).padStart(5, '0')}.jpg`;
      await page.screenshot({ path: path.join(dir, name), type: 'jpeg', quality: FULL ? 95 : 90 });
      if (i % 3 === 0) {
        // safe-zone check on settled frames (not during entrance animations)
        const t = i / tl.fps;
        const sc = tl.scenes.find((s) => s.start <= t && t < s.end);
        const nearPhrase = tl.phrases.some((p) => t >= p.start && t - p.start < 0.45);
        if (t - sc.start > 0.6 && !nearPhrase && !tl.cuts.some((c) => Math.abs(t - c) < 0.35)) {
          const bad = await page.evaluate(() => [...document.querySelectorAll('.cap div, .kw, .big, .bubble, .strip, .stamp, .heading h1, .url')]
            .flatMap((el) => { const rg = document.createRange(); rg.selectNodeContents(el); return [...rg.getClientRects()].filter((r) => r.width > 2); })
            .filter((r) => r.top < 230 || r.bottom > 1440 || r.left < 40 || (r.right > 940 && r.bottom > 700) || r.right > 1040)
            .map((r) => `[${Math.round(r.left)},${Math.round(r.top)}→${Math.round(r.right)},${Math.round(r.bottom)}]`));
          if (bad.length) issues.push(`${version} t=${t.toFixed(2)} ${sc.id}: ${bad.join(' ')}`);
        }
      }
    }
    await page.close();
    }
    if (!testTimes) {
      const finalDir = path.join(root, 'renders', 'final');
      fs.mkdirSync(finalDir, { recursive: true });
      const mp4 = FULL ? path.join(finalDir, `fanous_ad_${version}_1080x1920.mp4`) : path.join(out, `preview_${version}.mp4`);
      const venc = FULL
        ? ['-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '10', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p']
        : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p'];
      execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(tl.fps), '-i', path.join(dir, 'f%05d.jpg'), '-i', audio,
        '-map', '0:v', '-map', '1:a', ...venc, '-r', String(tl.fps),
        '-c:a', 'aac', '-b:a', FULL ? '256k' : '192k', '-ar', '48000', '-t', String(tl.duration), '-movflags', '+faststart', mp4]);
      console.log('wrote', mp4);
    }
  }
  await browser.close();
  if (issues.length) { console.error('SAFE-ZONE:\n' + issues.slice(0, 40).join('\n')); process.exitCode = 2; }
  console.log('done');
})().catch((e) => { console.error(e); process.exit(1); });
