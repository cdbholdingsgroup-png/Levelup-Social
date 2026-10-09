"""Turn a rendered post into a vertical video with music timed so the track's lift lands on the question slide.

Usage: python3 tools/make_video.py content/week1.json <day> "<track file in music/>" [lift_seconds]
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIFTS = {  # where each track picks up (seconds), measured from the audio
    "Aylex - A Positive Direction.mp3": 85, "Lukrembo - Bread.mp3": 112, "Pufino - Revelations.mp3": 55, "Sunova - Heroes.mp3": 9,
    "Pufino - Hopeful.mp3": 20, "Zambolino - First Days of Spring.mp3": 40, "Chill Pulse - Rise.mp3": 13,
}
XF = 0.5


def hold(s):
    words = len(json.dumps(s).split())
    return 4.5 if s["type"] == "cta" else min(9.0, max(5.0, 3.5 + words / 6))


def main(week_path, day, track, lift=None):
    week = json.load(open(week_path))
    post = next(p for p in week["posts"] if p["day"] == int(day))
    folder = os.path.join(ROOT, "posts", week["week"])
    durs = [hold(s) for s in post["slides"]]
    # slide where the music should lift: first question, else the last slide
    qi = next((i for i, s in enumerate(post["slides"]) if s["type"] == "question"), len(durs) - 1)
    q_start = sum(durs[:qi]) - XF * qi
    total = sum(durs) - XF * (len(durs) - 1)
    lift = LIFTS.get(track, 15) if lift is None else float(lift)
    start = max(0.0, lift - q_start)
    inputs, filt = [], []
    for i, d in enumerate(durs):
        inputs += ["-i", os.path.join(folder, f"day{post['day']}-slide{i+1}.jpg")]
        filt.append(f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0005,1.08)':x='iw/2-(iw/zoom/2)':"
                    f"y='ih/2-(ih/zoom/2)':d={int(d*30)}:s=1080x1920:fps=30,setsar=1[v{i}]")
    prev, off = "v0", 0.0
    for i in range(1, len(durs)):
        off += durs[i - 1] - XF
        filt.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    n = len(durs)
    filt.append(f"[{n}:a]afade=t=in:d=1.5,afade=t=out:st={total-2:.2f}:d=2[a]")
    out = os.path.join(ROOT, "video", week["week"].replace("/", "-"), f"day{post['day']}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-ss", f"{start:.2f}",
                    "-i", os.path.join(ROOT, "music", track), "-filter_complex", ";".join(filt),
                    "-map", f"[{prev}]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    print(f"{out}  {total:.1f}s  music from {start:.1f}s, lift on slide {qi+1}")


if __name__ == "__main__":
    main(*sys.argv[1:])
