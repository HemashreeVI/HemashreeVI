#!/usr/bin/env node
// Puts the day's koi (koi/koi.gif from the git-koi action) into an animated pond
// and writes koi/pond.webp. Needs Playwright (Chromium) and ffmpeg.
//
//   node scripts/koi_pond/render_pond.js
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const KOI = path.join(ROOT, 'koi', 'koi.gif'), OUT = path.join(ROOT, 'koi', 'pond.webp');

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pond-'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 520 } });
  await p.goto('file://' + path.join(__dirname, 'pond.html'));
  const n = await p.evaluate(b64 => window.load(b64), fs.readFileSync(KOI).toString('base64'));
  // the koi gif runs at 70 ms a frame: keep its timing so it swims at its own pace
  const delay = 70;
  for (let i = 0; i < n; i++) {
    const data = await p.evaluate(i => { window.renderFrame(i); return document.getElementById('c').toDataURL('image/png'); }, i);
    fs.writeFileSync(path.join(tmp, `f${String(i).padStart(4, '0')}.png`), Buffer.from(data.split(',')[1], 'base64'));
  }
  await b.close();
  execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(1000 / delay), '-i', path.join(tmp, 'f%04d.png'),
    '-c:v', 'libwebp_anim', '-lossless', '0', '-quality', '85', '-compression_level', '6', '-loop', '0', OUT], { stdio: 'inherit' });
  fs.rmSync(tmp, { recursive: true });
  console.log(`koi/pond.webp  ${n} frames  ${(fs.statSync(OUT).size / 1e6).toFixed(1)} MB`);
})();
