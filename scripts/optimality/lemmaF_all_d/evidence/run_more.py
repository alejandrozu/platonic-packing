"""Second batch of the evidence campaign (unrestricted search; the case RC4; the remaining case away from S = 2). Resumable."""
import os, subprocess, sys, math
from concurrent.futures import ThreadPoolExecutor
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
def B(d, big, mid, small): return big if d <= 10 else (mid if d <= 16 else small)
jobs = []
for d in list(range(3, 17)) + [20, 24]:
    jobs.append((f"free-{d}-1", f"search.py free {d} {B(d,512,256,128)} 1", "free.jsonl"))
for d in list(range(5, 17)) + [20, 24]:
    for sd in (1, 2): jobs.append((f"rc4-{d}-{sd}", f"search.py rc4 {d} {B(d,512,256,128)} {sd}", "rc4.jsonl"))
for d in (6, 8, 10, 12, 16):
    for sig in (2.1, 2.25, 2.5, 3.0):
        if sig < math.sqrt(d) - 0.05:
            jobs.append((f"rcS-{d}-{sig}", f"search.py rcS {d} {256 if d <= 10 else 128} 1 {sig}", "rcS.jsonl"))
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
