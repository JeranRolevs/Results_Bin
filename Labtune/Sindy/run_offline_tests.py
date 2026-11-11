"""Run each version in its own interpreter to prevent module-name collisions.
Only synthetic fixtures: no downloads, raw EEG, model APIs or provider calls.
"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
for folder in ("01-cap-absolute-bandpower", "02-cap-relative-bandpower"):
    print(f"\n=== {folder} ===", flush=True)
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / folder / "evaluator"), "-p", "test_*.py", "-v"], env=env, check=True)
