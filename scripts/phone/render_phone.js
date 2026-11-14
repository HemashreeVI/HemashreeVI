#!/usr/bin/env node
// Renders scripts/phone/phone.html at 2x and cuts it into README slices:
//   assets/phone/top-<hash>.png, app-<id>-<hash>.png (one per app), dots, dock-<id>, bottom
// plus assets/phone/manifest.json describing the layout.
//
//   node scripts/phone/render_phone.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..', '..'), OUT = path.join(ROOT, 'assets', 'phone');
(async () => {
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 400, height: 1200 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(__dirname, 'phone.html'));
  await p.evaluate(() => window.ready);
  const L = await p.evaluate(() => {
    const R = e => { const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
    const ph = R(document.getElementById('phone'));
    const apps = [...document.querySelectorAll('#grid .app')].map(e => ({ id: e.dataset.app, ...R(e) }));
    const dock = [...document.querySelectorAll('#dock .app')].map(e => ({ id: e.dataset.app, ...R(e) }));
    const sl = n => R(document.querySelector(`[data-slice=${n}]`));
    return { ph, apps, dock, dots: sl('dots'), dockBox: sl('dock'), bottom: sl('bottom'), grid: R(document.getElementById('grid')) };
  });
  const X0 = L.ph.x, X1 = L.ph.x + L.ph.w;
  // column cut lines: phone edges plus the midpoints between app columns
  const cols = [...new Set(L.apps.map(a => Math.round(a.x)))].sort((a, b) => a - b);
  const cuts = [X0, ...cols.slice(1).map((c, i) => (cols[i] + L.apps[0].w + c) / 2), X1];
  const rows = [...new Set(L.apps.map(a => Math.round(a.y)))].sort((a, b) => a - b);
  const man = { width: Math.round(L.ph.w), slices: [] };
  // file names carry a short content hash, so a changed slice gets a new URL and no cache shows an old one
  const shot = async (name, x, y, w, h) => {
    const buf = await p.screenshot({ clip: { x, y, width: w, height: h }, omitBackground: true });
    const file = name.replace('.png', '-' + crypto.createHash('sha1').update(buf).digest('hex').slice(0, 8) + '.png');
    fs.writeFileSync(path.join(OUT, file), buf);
    return { file, w: Math.round(w), h: Math.round(h) };
  };
  man.top = await shot('top.png', X0, L.ph.y, L.ph.w, L.grid.y - L.ph.y);
  man.rows = [];
  for (const [ri, y] of rows.entries()) {
    const rowApps = L.apps.filter(a => Math.round(a.y) === y).sort((a, b) => a.x - b.x);
    const h = rowApps[0].h, row = [];
    for (let c = 0; c < cuts.length - 1; c++) row.push({ id: rowApps[c].id, ...(await shot(`app-${rowApps[c].id}.png`, cuts[c], y, cuts[c + 1] - cuts[c], h)) });
    man.rows.push(row);
  }
  const lastRowEnd = rows[rows.length - 1] + L.apps[0].h;
  man.dots = await shot('dots.png', X0, lastRowEnd, L.ph.w, L.dockBox.y - lastRowEnd);
  const dcols = L.dock.map(d => d.x + d.w / 2);
  const dcuts = [X0, ...dcols.slice(1).map((c, i) => (dcols[i] + c) / 2), X1];
  man.dock = [];
  for (let c = 0; c < L.dock.length; c++) man.dock.push({ id: L.dock[c].id, ...(await shot(`dock-${L.dock[c].id}.png`, dcuts[c], L.dockBox.y, dcuts[c + 1] - dcuts[c], L.dockBox.h)) });
  man.bottom = await shot('bottom.png', X0, L.dockBox.y + L.dockBox.h, L.ph.w, L.ph.y + L.ph.h - (L.dockBox.y + L.dockBox.h));
  await p.screenshot({ path: path.join(OUT, 'full.png'), clip: { x: X0, y: L.ph.y, width: L.ph.w, height: L.ph.h }, omitBackground: true });
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(man, null, 1));
  await b.close();
  console.log(JSON.stringify(man.rows.map(r => r.map(s => `${s.id}:${s.w}x${s.h}`))), man.top, man.dots, man.bottom);
})();
