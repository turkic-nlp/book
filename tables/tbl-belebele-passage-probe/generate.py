from pathlib import Path
import runpy,sys
sys.argv=[sys.argv[0],Path(__file__).resolve().parent.name]
runpy.run_path(str(Path(__file__).resolve().parents[2]/"experiments/empirical-2026-10/build_assets.py"),run_name="__main__")
