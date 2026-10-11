"""Run the original analysis and save its console output and figures."""

# 아래 설정을 수정한 뒤 실행하세요. 드론 이름은 폴더 이름과 같아야 합니다.
DRONE = "DroneD"  # 예: "DroneA", "DroneB", "DroneD", "test"
LOGS = [74]  # None: 해당 기체의 모든 로그. 일부만 분석하려면 예: [100, 103]

from pathlib import Path
import contextlib
import runpy
import sys
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
drone_dir = root / DRONE
if not drone_dir.is_dir():
    raise SystemExit(f"드론 폴더가 없습니다: {drone_dir}")
if LOGS is None:
    log_paths = sorted(drone_dir.glob("*.ulg"))
else:
    if not isinstance(LOGS, list) or not LOGS or any(type(number) is not int for number in LOGS):
        raise SystemExit("LOGS에 None 또는 로그 번호 목록을 입력하세요. 예: [100, 103]")
    log_paths = []
    for number in dict.fromkeys(LOGS):
        matches = sorted(drone_dir.glob(f"log_{number}_*.ulg"))
        if len(matches) != 1:
            raise SystemExit(f"{DRONE}: log_{number}_*.ulg 파일이 정확히 하나 필요합니다. 발견: {len(matches)}개")
        log_paths.append(matches[0])
if not log_paths:
    raise SystemExit(f"분석할 .ulg 로그가 없습니다: {drone_dir}")

successful = 0
failed = []
for logfile in log_paths:
    output = drone_dir / "analysis" / logfile.stem / "current"
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
