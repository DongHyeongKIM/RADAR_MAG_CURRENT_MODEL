"""Run the original analysis and save its console output and figures."""
from pathlib import Path
import contextlib
import runpy
import sys
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
successful = 0
failed = []
for logfile in sorted((root / "DroneC").glob("*.ulg")):
    output = root / "DroneC" / "analysis" / logfile.stem / "current"
    sys.argv = [str(root / "mag_compensation.py"), str(logfile), "current", "--instance", "0"]
    print(f"Analyzing: {logfile.name}", flush=True)
    try:
        output.mkdir(parents=True, exist_ok=True)
        with (output / "results.txt").open("w", encoding="utf-8") as report:
            with contextlib.redirect_stdout(report), contextlib.redirect_stderr(report):
                try:
                    runpy.run_path(str(root / "mag_compensation.py"), run_name="__main__")
                    for number in plt.get_fignums():
                        plt.figure(number).savefig(output / f"figure_{number:02d}.png", dpi=120)
                except (Exception, SystemExit):
                    traceback.print_exc()
                    raise
    except (Exception, SystemExit) as error:
        failed.append(logfile.name)
        print(f"FAILED: {logfile.name}: {type(error).__name__}: {error}")
        print(f"Error details: {output / 'results.txt'}")
        continue
    else:
        successful += 1
        print((output / "results.txt").read_text(encoding="utf-8"))
        print(f"Saved results: {output}")
    finally:
        plt.close("all")

print(f"Finished: {successful} succeeded, {len(failed)} failed.")
for name in failed:
    print(f"  FAILED: {name}")
sys.exit(1 if failed else 0)
