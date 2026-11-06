#!/usr/bin/env node
// Renders scripts/intro/intro.html frame by frame and encodes
// assets/intro/hemashree-intro.mp4 (1920x800) and hemashree-intro.gif (900x375).
//
//   node scripts/intro/render_intro.js
//
// Needs Playwright (Chromium) and ffmpeg.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'assets', 'intro');
const FPS = 30;

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'intro-'));
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 800 } });
  await page.goto('file://' + path.join(__dirname, 'intro.html'));
  await page.evaluate(() => window.ready);
  const dur = await page.evaluate(() => window.DURATION);
  const frames = Math.round(dur * FPS);
  for (let i = 0; i < frames; i++) {
    const data = await page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, i / FPS);
    fs.writeFileSync(path.join(tmp, `f${String(i).padStart(4, '0')}.png`), Buffer.from(data.split(',')[1], 'base64'));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${frames}\n`);
  }
  await browser.close();
  const ff = (...a) => execFileSync('ffmpeg', ['-v', 'error', '-y', ...a], { stdio: 'inherit' });
  ff('-framerate', String(FPS), '-i', path.join(tmp, 'f%04d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
     '-crf', '20', '-preset', 'slow', '-movflags', '+faststart', path.join(OUT, 'hemashree-intro.mp4'));
  ff('-framerate', String(FPS), '-i', path.join(tmp, 'f%04d.png'), '-vf',
     'fps=10,scale=900:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
     '-loop', '0', path.join(OUT, 'hemashree-intro.gif'));
  fs.rmSync(tmp, { recursive: true });
  for (const f of ['hemashree-intro.mp4', 'hemashree-intro.gif'])
    console.log(f, (fs.statSync(path.join(OUT, f)).size / 1e6).toFixed(1), 'MB');
})();
