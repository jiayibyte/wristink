"""Encode consecutive CUA simulator captures using their actual capture timing.
No clock values or watch graphics are synthesized in this animation.
"""
from pathlib import Path
from PIL import Image
import json

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'dist/motion/continuous'
times=json.loads((folder/'times.json').read_text())
images=[Image.open(folder/t['file']).convert('RGB') for t in times]
assert all(im.size==images[0].size for im in images)
palette=images[0].quantize(colors=128)
frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
durations=[max(20,times[i+1]['at']-t['at']) for i,t in enumerate(times[:-1])]
durations.append(1000)
out=ROOT/'dist/RetroWorld-v1.1-motion.gif'
frames[0].save(out,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
with Image.open(out) as gif:
    assert gif.is_animated and gif.n_frames>=2
    print(f'Native simulator animation: {gif.n_frames} distinct frames, {sum(durations)} ms; {out.stat().st_size:,} bytes')
