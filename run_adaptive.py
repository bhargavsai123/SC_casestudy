"""Resume runner: executes only the adaptive stage (sections 17-21).

The main run and ablation artifacts from the 2026-10-20 sweep are already on disk,
so those switches are turned off after the config cell is evaluated.
"""
import os
import sys
import time
import traceback
from pathlib import Path

ROOT = Path("/Users/bhargav/Downloads/SC")
os.chdir(ROOT)
os.environ.setdefault("MPLBACKEND", "Agg")

import json

NB = json.loads((ROOT / "GAAPO_improved.ipynb").read_text())


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main():
    ns = {"__name__": "__main__", "__file__": str(ROOT / "run_adaptive.py")}
    t_all = time.time()
    for idx, cell in enumerate(NB["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if src.lstrip().startswith("%pip"):
            log(f"cell {idx}: skipped (magic)")
            continue
        log(f"cell {idx}: running")
        t0 = time.time()
        try:
            exec(compile(src, f"cell_{idx}", "exec"), ns)
        except Exception:
            log(f"cell {idx}: FAILED after {time.time() - t0:.1f}s")
            print(traceback.format_exc(), flush=True)
            return 1
        log(f"cell {idx}: ok ({time.time() - t0:.1f}s)")

        if idx == 5:
            ns.update(RUN_SMOKE_TEST=False, RUN_MAIN_EXPERIMENT=False,
                      RUN_ABLATION=False, RUN_SELECTION_COMPARISON=False)
            log("patched: main run, smoke test and ablation skipped "
                "(artifacts already on disk)")
    log(f"ADAPTIVE STAGE OK in {(time.time() - t_all) / 3600:.2f} h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
