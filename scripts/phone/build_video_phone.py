#!/usr/bin/env python3
"""Turns the screen recordings from record_screen.js into the README's second
phone: an animated WebP the same size as the clickable phone (380x953 design,
shown at 320px), with the same bezel, status bar and home bar.

    python3 scripts/phone/build_video_phone.py <recordings-dir>

Needs ffmpeg. Writes assets/phone/playing-<hash>.webp, playing-wide-<hash>.webp and video.json.
"""
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "assets" / "phone"
REC = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build" / "screen")
W, H, PAD, R_OUT, R_IN, BAR = 380, 953, 13, 52, 40, 44
SW, SH = W - 2 * PAD, H - 2 * PAD - BAR        # 354 x 883: the recording viewport
FPS, XF, QUALITY = 12, 0.5, 70               # frame rate, cross-slide between apps, WebP quality
MARGIN = 75                                    # wide copy: transparent margin on the right (~63px in the README)

OVERLAY = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><clipPath id="hole"><rect x="{PAD}" y="{PAD}" width="{SW}" height="{H - 2 * PAD}" rx="{R_IN}"/></clipPath></defs>
<path fill="#0A0A10" fill-rule="evenodd" d="M{R_OUT} 0H{W - R_OUT}A{R_OUT} {R_OUT} 0 0 1 {W} {R_OUT}V{H - R_OUT}A{R_OUT} {R_OUT} 0 0 1 {W - R_OUT} {H}H{R_OUT}A{R_OUT} {R_OUT} 0 0 1 0 {H - R_OUT}V{R_OUT}A{R_OUT} {R_OUT} 0 0 1 {R_OUT} 0Z
M{PAD + R_IN} {PAD}A{R_IN} {R_IN} 0 0 0 {PAD} {PAD + R_IN}V{H - PAD - R_IN}A{R_IN} {R_IN} 0 0 0 {PAD + R_IN} {H - PAD}H{W - PAD - R_IN}A{R_IN} {R_IN} 0 0 0 {W - PAD} {H - PAD - R_IN}V{PAD + R_IN}A{R_IN} {R_IN} 0 0 0 {W - PAD - R_IN} {PAD}Z"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{R_OUT - 1}" fill="none" stroke="#2A2A38" stroke-width="2"/>
<g clip-path="url(#hole)"><rect x="{PAD}" y="{PAD}" width="{SW}" height="{BAR}" fill="#000"/>
<rect x="{W / 2 - 65}" y="{H - PAD - 16}" width="130" height="5" rx="2.5" fill="#fff" fill-opacity=".85"/></g>
<text x="{PAD + 26}" y="{PAD + 27}" font-family="Inter,Helvetica,Arial,sans-serif" font-size="15" font-weight="600" fill="#fff">9:41</text>
<circle cx="{W / 2}" cy="{PAD + 22}" r="10" fill="#000" stroke="#1a1a24" stroke-width="2"/>
<g transform="translate({W - PAD - 26 - 70} {PAD + 16})" fill="#fff">
<rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5" width="3" height="7" rx="1"/><rect x="10" y="2.5" width="3" height="9.5" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/>
<path transform="translate(24 0)" d="M8 11.5L1 4.2a10 10 0 0 1 14 0Z"/>
<g transform="translate(44 0)"><rect x=".5" y=".5" width="22" height="11" rx="3" fill="none" stroke="#fff"/><rect x="2.5" y="2.5" width="16" height="7" rx="1.5" fill="#5EEAD4"/><rect x="23.5" y="4" width="2" height="4" rx="1"/></g></g>
<circle cx="{W - PAD - 26 - 84}" cy="{PAD + 22}" r="4" fill="#FF3B30"><animate attributeName="opacity" values="1;.2;1" dur="1s" repeatCount="indefinite"/></circle>
</svg>'''


def run(*a):
    subprocess.run(a, check=True)


def main():
    tmp = Path(tempfile.mkdtemp())
    (tmp / "overlay.svg").write_text(OVERLAY)
    # rasterise the overlay with Chromium (keeps fonts and anti-aliasing identical to the left phone)
    run("node", "-e", f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});
await p.goto('file://{tmp}/overlay.svg');await p.screenshot({{path:'{tmp}/overlay.png',omitBackground:true}});await b.close();}})();""")
    segs = []
    for name in ("portfolio", "gitloom"):
        d = REC / name
        frames = json.loads((d / "frames.json").read_text())
        lst = tmp / f"{name}.txt"
        with lst.open("w") as f:
            for (a, ta), (_, tb) in zip(frames, frames[1:] + [[None, frames[-1][1] + .1]]):
                f.write(f"file '{d / a}'\nduration {max(tb - ta, 0.001):.4f}\n")
            f.write(f"file '{d / frames[-1][0]}'\n")
        out = tmp / f"{name}.mkv"
        run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-vf", f"scale={SW}:{SH}:flags=lanczos,fps={FPS}", "-c:v", "ffv1", "-pix_fmt", "bgr0", str(out))
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                   capture_output=True, text=True).stdout)
        segs.append((out, dur))
    (a, da), (b, db) = segs
    screen = tmp / "screen.mkv"
    run("ffmpeg", "-v", "error", "-y", "-i", str(a), "-i", str(b), "-filter_complex",
        f"[0][1]xfade=transition=slideleft:duration={XF}:offset={da - XF:.2f}", "-c:v", "ffv1", "-pix_fmt", "bgr0", str(screen))
    # animated WebP: same look as a GIF in a README, a fraction of the size for scrolling photos
    gif = tmp / "playing.webp"
    run("ffmpeg", "-v", "error", "-y", "-i", str(screen), "-loop", "1", "-i", str(tmp / "overlay.png"), "-filter_complex",
        f"color=c=black@0:s={W}x{H},format=rgba[bg];[bg][0]overlay={PAD}:{PAD + BAR}:shortest=1[s];[s][1]overlay=0:0:shortest=1,format=yuva420p",
        "-c:v", "libwebp_anim", "-lossless", "0", "-quality", str(QUALITY), "-compression_level", "6", "-loop", "0", str(gif))
    # a second copy with a transparent margin on the right, used on wide screens so the
    # two phones sit centred as a pair instead of the playing one hugging the edge
    wide = tmp / "playing-wide.webp"
    run("ffmpeg", "-v", "error", "-y", "-i", str(screen), "-loop", "1", "-i", str(tmp / "overlay.png"), "-filter_complex",
        f"color=c=black@0:s={W + MARGIN}x{H},format=rgba[bg];[bg][0]overlay={PAD}:{PAD + BAR}:shortest=1[s];[s][1]overlay=0:0:shortest=1,format=yuva420p",
        "-c:v", "libwebp_anim", "-lossless", "0", "-quality", str(QUALITY), "-compression_level", "6", "-loop", "0", str(wide))
    for old in [*OUT.glob("playing-*.gif"), *OUT.glob("playing-*.webp")]:
        old.unlink()
    pj = OUT / "video.json"
    info = {}
    for key, f in (("playing", gif), ("playing_wide", wide)):
        data = f.read_bytes()
        name = f"{key.replace('_', '-')}-{hashlib.sha1(data).hexdigest()[:8]}.webp"
        (OUT / name).write_bytes(data)
        info[key] = name
        print(f"  {name}  {len(data) / 1e6:.1f} MB")
    pj.write_text(json.dumps(info, indent=1))
    print(f"  {W}x{H}, {da + db - XF:.1f}s")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
