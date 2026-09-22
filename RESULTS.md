# 분석 결과 정리

기존 summary.json의 armed 구간 선택 자력계(vehicle_magnetometer) 회귀 기울기를 정리했습니다. 단위는 G/kA이며 공통 전류 범위 값이 있으면 이를 사용합니다.

| 기체 | 로그 | 보상 설정 | 전류 범위 (A) | X | Y | Z | 결과 |
|---|---|---|---|---|---|---|---|
| DroneA | 143 | 0 | 2.02–42.51 | -2.724 | 1.454 | 15.598 | [JSON](DroneA/analysis/log143_vs_log148/summary.json) |
| DroneA | 148 | 2 | 2.02–42.51 | 0.162 | -0.221 | -0.445 | [JSON](DroneA/analysis/log143_vs_log148/summary.json) |
| DroneB | 93 | 0 | 1.20–41.14 | -2.354 | -4.964 | 9.845 | [JSON](DroneB/analysis/log93_vs_log101/summary.json) |
| DroneB | 101 | 2 | 1.20–41.14 | 0.092 | -0.338 | -0.348 | [JSON](DroneB/analysis/log93_vs_log101/summary.json) |
| DroneB | 93 | 0 | 전체 armed | -2.354 | -4.964 | 9.845 | [JSON](DroneB/analysis/log93_vs_log97/summary.json) |
| DroneB | 97 | 0 | 전체 armed | -2.158 | -5.083 | 8.993 | [JSON](DroneB/analysis/log93_vs_log97/summary.json) |
| DroneC | 100 | 0 | 1.76–40.99 | -4.638 | -2.597 | 7.260 | [JSON](DroneC/analysis/log100_vs_log103/summary.json) |
| DroneC | 103 | 2 | 1.76–40.99 | 0.132 | -0.673 | -0.369 | [JSON](DroneC/analysis/log100_vs_log103/summary.json) |
| DroneD | 72 | 0 | 0.23–37.74 | -4.157 | -4.252 | 7.175 | [JSON](DroneD/analysis/log72_vs_log76/summary.json) |
| DroneD | 76 | 2 | 0.23–37.74 | 0.126 | 0.348 | 0.464 | [JSON](DroneD/analysis/log72_vs_log76/summary.json) |

보상 설정은 CAL_MAG_COMP_TYP입니다. DroneA 143→148, DroneB 93→101, DroneC 100→103, DroneD 72→76에서 0→2로 바뀌었고 공통 전류 범위의 X/Y/Z 모든 축에서 기울기 절댓값이 감소했습니다. DroneB 93→97은 두 로그 모두 0이므로 보상 전후 비교가 아닙니다.

이는 기록된 자력계 출력의 전류 의존성이 감소한 관찰 결과입니다. 로그 사이 자세·환경·전류 분포 차이가 포함되므로 비행 성능 개선이나 보상만의 인과 효과를 단정하지 않습니다.

## 비교 그래프

각 JSON에는 보상 파라미터, 센서 ID, 원시 센서 통계, 선택 자력계 통계와 추정 자세 범위가 들어 있습니다.

### DroneA / log143_vs_log148

- [전류·원시 자력계·추정 자세 시계열](DroneA/analysis/log143_vs_log148/recorded_timeseries.png)
- [원시 자력계 대 전류](DroneA/analysis/log143_vs_log148/raw_mag_vs_current.png)
- [선택 자력계 대 전류](DroneA/analysis/log143_vs_log148/selected_mag_vs_current.png)
- [선택 자력계 시계열](DroneA/analysis/log143_vs_log148/selected_mag_vs_time.png)

### DroneB / log93_vs_log101

- [전류·원시 자력계·추정 자세 시계열](DroneB/analysis/log93_vs_log101/recorded_timeseries.png)
- [원시 자력계 대 전류](DroneB/analysis/log93_vs_log101/raw_mag_vs_current.png)
- [선택 자력계 대 전류](DroneB/analysis/log93_vs_log101/selected_mag_vs_current.png)
- [선택 자력계 시계열](DroneB/analysis/log93_vs_log101/selected_mag_vs_time.png)

### DroneB / log93_vs_log97

- [전류·원시 자력계·추정 자세 시계열](DroneB/analysis/log93_vs_log97/recorded_timeseries.png)
- [원시 자력계 대 전류](DroneB/analysis/log93_vs_log97/raw_mag_vs_current.png)
- [선택 자력계 대 전류](DroneB/analysis/log93_vs_log97/selected_mag_vs_current.png)

### DroneC / log100_vs_log103

- [전류·원시 자력계·추정 자세 시계열](DroneC/analysis/log100_vs_log103/recorded_timeseries.png)
- [원시 자력계 대 전류](DroneC/analysis/log100_vs_log103/raw_mag_vs_current.png)
- [선택 자력계 대 전류](DroneC/analysis/log100_vs_log103/selected_mag_vs_current.png)
- [선택 자력계 시계열](DroneC/analysis/log100_vs_log103/selected_mag_vs_time.png)

### DroneD / log72_vs_log76

- [전류·원시 자력계·추정 자세 시계열](DroneD/analysis/log72_vs_log76/recorded_timeseries.png)
- [원시 자력계 대 전류](DroneD/analysis/log72_vs_log76/raw_mag_vs_current.png)
- [선택 자력계 대 전류](DroneD/analysis/log72_vs_log76/selected_mag_vs_current.png)
- [선택 자력계 시계열](DroneD/analysis/log72_vs_log76/selected_mag_vs_time.png)

## 보존한 오류 및 자료 범위

- test/analysis의 log_61_2026-9-21-08-34-28, log_64_2026-9-22-14-52-28, log_65_2026-9-22-14-55-48, log_65_2026-9-22-15-00-10 기록에는 전류 신호 부재로 인한 분석 실패가 있습니다.
- DroneB/analysis/log_93_2026-9-22-15-53-36/current/results.txt에는 PNG 저장 중 OSError가 남아 있습니다. 현재 그림 파일이 존재해도 해당 실행 기록을 완전 성공으로 분류하지 않았습니다.
- test/analysis에는 현재 test 폴더의 원본 목록과 일치하지 않는 과거 결과도 있습니다. log_61 원본은 이 작업 폴더에 없고 log_92/93/94 원본은 DroneB에 있습니다.
- DroneA의 날짜 미상 log_148 파일명과 원본은 그대로 보존했습니다.
- 기존 결과를 재계산하거나 덮어쓰지 않고 정리했습니다. 단일 로그 분석 결과는 각 analysis/<로그 이름>/current/의 results.txt와 figure_*.png에 있습니다.
