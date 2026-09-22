"""Compare recorded drone logs; no parameters are written to the vehicle."""

# 아래 두 줄만 수정한 뒤 실행하세요. 드론 이름은 폴더 이름과 같아야 합니다.
DRONE = 'DroneC'  # 예: 'DroneA', 'DroneB', 'DroneD'
LOGS = [100, 103]  # 비교할 로그 번호 두 개

from pathlib import Path
import json
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyulog import ULog

ROOT = Path(__file__).resolve().parent
if len(LOGS) != 2 or any(type(number) is not int for number in LOGS):
    raise SystemExit('LOGS에 로그 번호 두 개를 정수로 입력하세요. 예: [143, 148]')
DRONE_DIR = ROOT / DRONE
if not DRONE_DIR.is_dir():
    raise SystemExit(f'드론 폴더가 없습니다: {DRONE_DIR}')
log_paths = []
for number in LOGS:
    matches = sorted(DRONE_DIR.glob(f'log_{number}_*.ulg'))
    if len(matches) != 1:
        raise SystemExit(f'{DRONE}: log_{number}_*.ulg 파일이 정확히 하나 필요합니다. 발견: {len(matches)}개')
    log_paths.append(matches[0])
OUT = DRONE_DIR / 'analysis' / f'log{LOGS[0]}_vs_log{LOGS[1]}'
OUT.mkdir(parents=True, exist_ok=True)
def save_figure(figure, name):
    # Write a complete new file before replacing a previous plot.
    with tempfile.NamedTemporaryFile(dir=OUT, suffix='.png', delete=False) as stream:
        temporary = Path(stream.name)
        figure.savefig(stream, format='png', dpi=150)
    temporary.replace(OUT / name)

summary = {}
selected_samples = {}
fig, axes = plt.subplots(4, 2, figsize=(14, 13))
scatter, sax = plt.subplots(2, 3, figsize=(15, 8))
processed, pax = plt.subplots(1, 3, figsize=(15, 4))
processed_time, tax = plt.subplots(4, 2, figsize=(14, 11), sharex='col', sharey='row')
processed_time.suptitle('Recorded vehicle_magnetometer vs time\nShaded areas: armed; equal vertical scales across logs')
for col, number in enumerate(LOGS):
    path = log_paths[col]
    u = ULog(str(path))
    status = u.get_dataset('vehicle_status').data
    def armed(t):
        ix = np.searchsorted(status['timestamp'], t, side='right') - 1
        return (ix >= 0) & (status['arming_state'][np.maximum(ix, 0)] == 2)
    battery = u.get_dataset('battery_status', 0).data
    def current(t):
        return np.interp(t, battery['timestamp'], battery['current_a'])
    base = u.start_timestamp
    info = {'file': path.name, 'parameters': {k: float(v) for k, v in u.initial_parameters.items() if k.startswith('CAL_MAG')},
            'changed_parameters': u.changed_parameters, 'raw_sensors': {}}
    mask = armed(battery['timestamp'])
    info['armed_current_range_A'] = [float(np.min(battery['current_a'][mask])), float(np.max(battery['current_a'][mask]))]
    axes[0, col].plot((battery['timestamp']-base)*1e-6, battery['current_a'])
    axes[0, col].set(title=f'Log {number}: CAL_MAG_COMP_TYP={u.initial_parameters["CAL_MAG_COMP_TYP"]}', ylabel='Current [A]')
    for instance in (0, 1):
        data = u.get_dataset('sensor_mag', instance).data
        m = armed(data['timestamp'])
        amps = current(data['timestamp'][m])
        values = np.column_stack([data[a][m] for a in 'xyz'])
        slopes = np.polyfit(amps, values, 1)[0]
        info['raw_sensors'][str(instance)] = {'device_id': int(data['device_id'][0]), 'samples': int(m.sum()),
            'slope_G_per_kA': (slopes*1000).tolist(), 'std_G': values.std(axis=0).tolist(),
            'range_G': np.ptp(values, axis=0).tolist()}
        for axis, a in enumerate('xyz'):
            sax[instance, axis].scatter(amps, values[:, axis], s=6, alpha=.5, label=f'Log {number}')
            sax[instance, axis].set(title=f'MAG{instance} {a.upper()} (raw, armed)', xlabel='Current [A]', ylabel='Magnetic field [G]')
            axes[instance+1, col].plot((data['timestamp']-base)*1e-6, data[a], label=a.upper())
        axes[instance+1, col].set(ylabel=f'MAG{instance} raw [G]')
        axes[instance+1, col].legend()
    selected = u.get_dataset('vehicle_magnetometer').data
    m = armed(selected['timestamp'])
    vals = np.column_stack([selected[f'magnetometer_ga[{i}]'][m] for i in range(3)])
    info['selected_device_ids'] = [int(x) for x in np.unique(selected['device_id'])]
    color = f'C{col}'
    tax[0, col].plot((battery['timestamp'].astype(float)-base)*1e-6,
                     battery['current_a'], color=color)
    tax[0, col].set(title=f'Log {number} | CAL_MAG_COMP_TYP={u.initial_parameters["CAL_MAG_COMP_TYP"]}',
                    ylabel='Current [A]')
    # Plot recorded output directly, including disarmed portions; no refitting.
    mag_time = (selected['timestamp'].astype(float)-base)*1e-6
    for i, axis in enumerate('XYZ'):
        tax[i+1, col].plot(mag_time, selected[f'magnetometer_ga[{i}]'],
                           color=color, marker='.', markersize=3, linewidth=1,
                           label=f'Log {number}: recorded output')
        tax[i+1, col].set_ylabel(f'Mag {axis} [G]')
        tax[i+1, col].legend(loc='best', fontsize=8)
    # State changes define shaded intervals without interpolating arm state.
    state = status['arming_state'] == 2
    boundaries = np.r_[0, np.flatnonzero(state[1:] != state[:-1])+1, len(state)]
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        if state[start]:
            left = (float(status['timestamp'][start])-base)*1e-6
            right = (float(status['timestamp'][end]) if end < len(state) else u.last_timestamp)-base
            for ax in tax[:, col]:
                ax.axvspan(left, right*1e-6, color=color, alpha=.08)
    tax[3, col].set_xlabel('Time from each log start [s]')
    for ax in tax[:, col]:
        ax.grid(alpha=.2)
    info['selected_armed_slope_G_per_kA'] = (np.polyfit(current(selected['timestamp'][m]), vals, 1)[0]*1000).tolist()
    info['selected_armed_std_G'] = vals.std(axis=0).tolist()
    selected_samples[str(number)] = (current(selected['timestamp'][m]), vals)
    for i, axis in enumerate('XYZ'):
        pax[i].scatter(current(selected['timestamp'][m]), vals[:, i], s=12, alpha=.65, label=f'Log {number}')
        pax[i].set(title=f'Selected mag {axis} (vehicle_magnetometer)', xlabel='Current [A]', ylabel='Magnetic field [G]')
    attitude = u.get_dataset('vehicle_attitude').data
    w,x,y,z = [attitude[f'q[{i}]'].astype(float) for i in range(4)]
    euler = np.column_stack((np.arctan2(2*(w*x+y*z),1-2*(x*x+y*y)), np.arcsin(np.clip(2*(w*y-z*x),-1,1)), np.unwrap(np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z))))) * 180/np.pi
    info['estimated_attitude_armed_range_deg_RPY'] = np.ptp(euler[armed(attitude['timestamp'])], axis=0).tolist()
    for i, label in enumerate(('Roll','Pitch','Yaw')):
        axes[3,col].plot((attitude['timestamp']-base)*1e-6, euler[:,i], label=label)
    axes[3,col].set(xlabel='Time from log start [s]', ylabel='Estimated attitude [deg]')
    axes[3,col].legend()
    summary[str(number)] = info
for ax in sax.flat:
    ax.legend()
    ax.grid(alpha=.2)
fig.tight_layout()
scatter.tight_layout()
save_figure(fig, 'recorded_timeseries.png')
save_figure(scatter, 'raw_mag_vs_current.png')
for ax in pax:
    ax.legend()
    ax.grid(alpha=.2)
processed.tight_layout()
save_figure(processed, 'selected_mag_vs_current.png')
processed_time.tight_layout(rect=(0, 0, 1, .94))
save_figure(processed_time, 'selected_mag_vs_time.png')
low = max(v['armed_current_range_A'][0] for v in summary.values())
high = min(v['armed_current_range_A'][1] for v in summary.values())
for number, (amps, vals) in selected_samples.items():
    keep = (amps >= low) & (amps <= high)
    summary[number]['common_current_range_A'] = [low, high]
    summary[number]['common_current_slope_G_per_kA'] = (np.polyfit(amps[keep], vals[keep], 1)[0]*1000).tolist()
    summary[number]['common_current_std_G'] = vals[keep].std(axis=0).tolist()
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
