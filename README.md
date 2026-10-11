# RADAR_MAG_CURRENT_MODEL
PX4 magnetometer and current mapping.

드론별 PX4 ULog 비행 로그와 전류 기반 자력계 보상 분석을 모은 작업 저장소입니다. 2026-09-22 작업 폴더를 기준으로 원본 로그, 분석 코드, 수치 결과 및 그래프를 보존합니다. 일부 로그 파일명은 2026-09-21 또는 날짜 미상입니다.

## 자료 구성

- `DroneA/`, `DroneB/`, `DroneC/`, `DroneD/`: 기체별 원본 `.ulg`와 `analysis/` 결과
- `test/`: 초기 시험 로그 및 기존 분석·실패 기록
- `mag_compensation.py`: 전류 또는 추력에 따른 자력계 선형 보상 계수 계산
- `run_mag_analysis.py`: 분석 콘솔 출력과 그래프 일괄 저장 (현재 대상: DroneC)
- `compare_drone.py`: 두 로그의 원시/선택 자력계, 전류, 추정 자세 비교 (현재 대상: DroneC 100/103)
- [RESULTS.md](RESULTS.md): 기체별 비교 수치, 그래프 링크, 기존 실패 기록 정리

원본 로그 21개, PNG 그래프 103개, TXT 기록 27개, JSON 비교 결과 5개를 포함합니다. 로컬 Python 실행 환경과 다운로드 캐시는 `.gitignore`로 제외합니다.

## 실행

Python 3.12 환경에서 사용했습니다. 저장된 결과는 재실행 없이 열어볼 수 있습니다.

```bash
python -m venv .venv
# Windows PowerShell
.venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt
python mag_compensation.py DroneC/log_100_2026-9-21-22-23-42.ulg current --instance 0
python run_mag_analysis.py
python compare_drone.py
```

`--instance`는 전류/추력 신호 인스턴스입니다. 다른 기체를 비교하려면 `compare_drone.py` 상단의 `DRONE`과 `LOGS`를 수정합니다. 일괄 분석 대상은 `run_mag_analysis.py`의 두 `DroneC` 경로에서 변경합니다. 재실행하면 해당 결과 경로의 파일을 갱신합니다.

분석 코드는 로그를 읽어 결과를 생성하며 기체에 파라미터를 쓰지 않습니다. `mag_compensation.py`의 원저자 표기는 파일 헤더에 보존되어 있습니다.
