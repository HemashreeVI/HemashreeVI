#!/usr/bin/env node
// Renders every project card (assets/cards/show-*.svg) to a WebP next to it. The README uses the WebP:
// a plain image shows the same in every browser and in the GitHub mobile app, while an SVG with a
// screenshot inside it can be blocked by stricter image viewers. Needs Playwright and Pillow.
//   python3 scripts/build_cards.py && node scripts/cards_to_webp.js
//   CARD_MODE=light python3 scripts/build_cards.py && node scripts/cards_to_webp.js light
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const dir = path.join(__dirname, '..', 'assets', 'cards', process.argv[2] || '');
(async () => {
  const cards = fs.readdirSync(dir).filter(f => /^show-.*\.svg$/.test(f));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 600, height: 492 }, deviceScaleFactor: 2 });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'cards-'));
  for (const f of cards) {
    await p.goto('file://' + path.join(dir, f));
    await p.waitForTimeout(300);
    await p.screenshot({ path: path.join(tmp, f.replace('.svg', '.png')), omitBackground: true });
  }
  await b.close();
  execFileSync('python3', ['-c', `
import sys, glob, os
from PIL import Image
for f in glob.glob(sys.argv[1] + '/*.png'):
    Image.open(f).save(os.path.join(sys.argv[2], os.path.basename(f)[:-4] + '.webp'), quality=88, method=6)
`, tmp, dir]);
  fs.rmSync(tmp, { recursive: true });
  console.log(`${cards.length} cards rendered to WebP`);
})();
