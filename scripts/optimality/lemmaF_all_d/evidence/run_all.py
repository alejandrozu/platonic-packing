"""Run the evidence campaign with two workers. Resumable: finished jobs are listed in done.txt."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
def B(d, big, mid, small): return big if d <= 10 else (mid if d <= 16 else small)
jobs = []
for d in list(range(3, 17)) + [20, 24, 32]:
    for s in (1, 2): jobs.append((f"global-{d}-{s}", f"search.py global {d} {B(d,512,256,128)} {s}", "global.jsonl"))
for d in list(range(5, 17)) + [20, 24]:
    for s in (1, 2): jobs.append((f"rc-{d}-{s}", f"search.py rc {d} {B(d,512,256,128)} {s}", "rc.jsonl"))
for d in range(3, 17):
    taus = sorted(set([round(1 - 1 / (d - 1), 12)] + [t for t in (0.9, 0.75, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1) if t >= 1 / d + 0.01]), reverse=True)
    for t in taus: jobs.append((f"far-{d}-{t}", f"search.py far {d} {128 if d <= 10 else 64} 1 {t}", "far.jsonl"))
for d in range(3, 13):
    jobs.append((f"frames-{d}", f"frames.py {d} {96 if d <= 8 else 48} {d}", "frames.jsonl"))
done = set(open("done.txt").read().split()) if os.path.exists("done.txt") else set()
todo = [j for j in jobs if j[0] not in done]
env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
def work(job):
    jid, cmd, out = job
    r = subprocess.run([sys.executable] + cmd.split(), capture_output=True, text=True, env=env)
    if r.returncode == 0:
        with open(out, "a") as f: f.write(r.stdout)
        with open("done.txt", "a") as f: f.write(jid + "\n")
    else:
        with open("errors.log", "a") as f: f.write(jid + "\n" + r.stderr[-2000:] + "\n")
    return jid
print(len(jobs), "jobs,", len(todo), "to do", flush=True)
with ThreadPoolExecutor(2) as ex:
    for jid in ex.map(work, todo): print("done", jid, flush=True)
print("ALL_DONE", flush=True)
