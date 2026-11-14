#!/usr/bin/env node
// Records what plays on the README's second phone: real screen recordings of
// the portfolio (F1 lights intro, profile picker, scroll) and GitLoom, at a
// phone-sized viewport. Needs local clones of HemashreeVI.github.io and GitLoom
// next to this repo (../HemashreeVI.github.io, ../gitloom).
//
//   node scripts/phone/record_screen.js <out-dir>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..'), PARENT = path.dirname(ROOT);
const OUT = path.resolve(process.argv[2] || path.join(ROOT, 'build', 'screen'));
const VIEW = { width: 354, height: 883 };

async function smoothScroll(p, to, ms) {
  await p.evaluate(([to, ms]) => new Promise(res => {
    const from = scrollY, t0 = performance.now();
    const ease = x => x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
    (function step(now) { const k = Math.min(1, (now - t0) / ms); scrollTo(0, from + (to - from) * ease(k)); k < 1 ? requestAnimationFrame(step) : res(); })(t0);
  }), [to, ms]);
}

// Chrome's screencast gives frames at device-pixel resolution with timestamps;
// they're saved as PNGs plus a list of their times, turned into video later.
async function record(b, name, url, script) {
  const dir = path.join(OUT, name); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const ctx = await b.newContext({ viewport: VIEW, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  const frames = [];
  cdp.on('Page.screencastFrame', f => {
    const file = `f${String(frames.length).padStart(5, '0')}.jpg`;
    fs.writeFileSync(path.join(dir, file), Buffer.from(f.data, 'base64'));
    frames.push([file, f.metadata.timestamp]);
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  await p.goto(url);
  await p.addStyleTag({ content: 'html,body{scroll-behavior:auto!important}' });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: VIEW.width * 2, maxHeight: VIEW.height * 2, everyNthFrame: 1 });
  const marks = await script(p);
  await cdp.send('Page.stopScreencast');
  await ctx.close();
  fs.writeFileSync(path.join(dir, 'frames.json'), JSON.stringify(frames));
  return { ...marks, frames: frames.length, seconds: frames.length ? +(frames.at(-1)[1] - frames[0][1]).toFixed(2) : 0 };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const marks = {};
  marks.portfolio = await record(b, 'portfolio', 'file://' + path.join(PARENT, 'hemashreevi.github.io', 'index.html'), async p => {
    // F1 lights intro plays by itself
    await p.waitForTimeout(6600);              // ...then "Who's on the grid today?"
    await p.getByText('Recruiter', { exact: true }).first().tap();
    await p.waitForTimeout(2200);              // billboard
    await smoothScroll(p, 2400, 5200);
    await p.waitForTimeout(700);
    await smoothScroll(p, 5200, 4200);
    await p.waitForTimeout(900);
    return {};
  });
  marks.gitloom = await record(b, 'gitloom', 'file://' + path.join(PARENT, 'gitloom', 'index.html'), async p => {
    await p.waitForTimeout(400);
    await p.waitForTimeout(1600);
    await smoothScroll(p, 1700, 3200);
    await p.waitForTimeout(800);
    return {};
  });
  await b.close();
  fs.writeFileSync(path.join(OUT, 'marks.json'), JSON.stringify(marks, null, 1));
  console.log(JSON.stringify(marks));
})();
