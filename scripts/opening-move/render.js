// Renders "The Opening Move" (film.html) frame by frame in headless Chromium and writes
// assets/intro/opening-move.webp (README, 1100x458, looping) and opening-move.mp4.
//   node scripts/opening-move/render.js          needs: playwright, ffmpeg, python3 + Pillow
//   node scripts/opening-move/render.js 10.5     only saves the frame at 10.5s (for checking)
// The photos in photos/ were generated with ChatGPT; film.html adds the camera moves, cuts, labels and timing.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const OUT = path.resolve(__dirname, '../../assets/intro'), FPS = 20;

(async () => {
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1100, height: 458 } });
  await p.goto('file://' + path.join(__dirname, 'film.html'));
  await p.evaluate(() => window.ready);
  const stage = await p.$('#stage'), one = process.argv[2];
  if (one) { await p.evaluate(t => render(t), +one); await stage.screenshot({ path: `frame-${one}.png` }); return b.close(); }
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opening-move-'));
  const n = await p.evaluate(() => DUR) * FPS;
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => render(t), i / FPS);
    await stage.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
  }
  await b.close();
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-movflags', '+faststart', path.join(OUT, 'opening-move.mp4')]);
  // animated WebP: every frame stored whole (no blending), so dark areas stay clean
  execFileSync('python3', ['-c', `
import glob, sys
from PIL import Image
fr = [Image.open(f).convert('RGB') for f in sorted(glob.glob(sys.argv[1] + '/*.png'))]
fr[0].save(sys.argv[2], save_all=True, append_images=fr[1:], duration=${1000 / FPS}, loop=0, quality=80, method=6, allow_mixed=False, minimize_size=False)`,
    dir, path.join(OUT, 'opening-move.webp')]);
  fs.rmSync(dir, { recursive: true });
  for (const f of ['opening-move.webp', 'opening-move.mp4']) console.log(f, (fs.statSync(path.join(OUT, f)).size / 1e6).toFixed(1), 'MB');
})();
