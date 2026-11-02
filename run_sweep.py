"""Headless runner: execute GAAPO_improved.ipynb cells with the real clients.

Equivalent to `Run All` but without a Jupyter kernel, so the deliverable notebook
keeps no stored outputs. Writes artifacts under content/gaapo_outputs_v2/.
"""
import json
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path("/Users/bhargav/Downloads/SC")
os.chdir(ROOT)
os.environ.setdefault("MPLBACKEND", "Agg")

NB = json.loads((ROOT / "GAAPO_improved.ipynb").read_text())


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    ns = {"__name__": "__main__", "__file__": str(ROOT / "run_sweep.py")}
    total = len(NB["cells"])
    skipped = 0
    t_all = time.time()

    for idx, cell in enumerate(NB["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if source.lstrip().startswith("%pip"):
            skipped += 1
            log(f"cell {idx}: skipped (magic)")
            continue
        log(f"cell {idx}/{total}: running")
        t0 = time.time()
        try:
            exec(compile(source, f"cell_{idx}", "exec"), ns)
        except Exception:
            log(f"cell {idx}: FAILED after {time.time() - t0:.1f}s")
            print(traceback.format_exc(), flush=True)
            return 1
        log(f"cell {idx}: ok ({time.time() - t0:.1f}s)")

    log(f"ALL CELLS OK in {(time.time() - t_all) / 3600:.2f} h "
        f"({skipped} magic cells skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
